<!--
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

[[_TOC_]]

# AI as a Service

This project contain the code for validation and pollution computing for the OpenDataHub data about A22 traffic.

The TrafficData is periodically pulled from the A22 collection, data validation evaluated and the pollution data is estimated and pushed back on the OpenDataHub.

## Project detail

### Architecture

![project structure](/pollution_v2/documentation/UML Architecture.png)

**Components**:

- *Jobs*: `validator`, `pollution-computer`, `road-weather` and `pollution-dispersal` are independent, containerized entry points (`src/<job>/main.py`), each on its own cron schedule. Locally, `docker-compose.yml` runs each job's container with `supercronic` handling the schedule; in the cluster, each job is a Kubernetes `CronJob` (see `infrastructure/helm`).
- *Data validator*: This component downloads traffic data from ODH, validates them and upload them again into ODH.
- *Pollution computer*: This task handles the computation of a batch of measures. It downloads the traffic data from the OpenDataHub (Using the TrafficMeasure connector), computes the pollution measures (using the Pollution Computation Model) and it uploads the new measure to the ODH using the PollutionMeasure connector.

#### Validation Algorithm Criteria

The validation algorithm is designed to assign a validity flag (`is_valid`) to traffic data, which can be either 1 (valid), 0 (not valid) or 999 (None). This flag is determined through a three-layer validation process:

1. **Layer 1 - Daily traffic volume assessment at individual stations**  
   This layer compares the total number of vehicles recorded at a monitoring station throughout the day against statistically derived historical data. If historical data is unavailable for a specific station, data from neighboring stations is used, assuming similar average behavior. The statistical comparison uses the Z-score method, which assesses how much the current value deviates from a reference parameter. This parameter is historically determined based on the day type (weekday or holiday) and the time of year. The calculated Z-score is compared to an acceptable range defined by lower and upper boundaries.

   1. **Layer 1.1 - Consistency check with adjacent sations**
      If a daily data set is flagged as invalid by Layer 1, an additional check evaluates whether the anomaly detected at one station systematically occurs at neighboring stations. This helps identify potential false positives, particularly when anomalies might be due to genuine, significant changes in road conditions rather than data errors. Here, the Z-score method is also used, but the reference parameter is based on values observed at adjacent stations instead of historical data.

2. **Layer 2 - Daily traffic volume evaluation on individual lanes**
   This layer mirrors Layer 1 but focuses on the ratio of daily traffic volumes between driving and passing lanes. This ratio is compared with historical data. This validation criterion helps detect anomalies in a single lane's traffic sensor that aren't significant enough to cause a Layer 1 validation failure.

3. **Layer 3 - Time series anomalies**
   Layer 3 assesses the consistency of daily time series data, identifying anomalies such as sudden increases or decreases and persistent null values.

Each layer assigns a validation flag to the data, which are then combined to determine a final, unified validation state.

The validation parameters are defined in the file `pollution_v2/src/config/validator.yaml`. The Z-score limit parameters can be set to *null* to effectively disable their influence.

| Layer | Parameter | Description                                                                             | Default |
|-------|-----------|-----------------------------------------------------------------------------------------|---------|
| 1     | low       | Lower limit of the Z-score                                                              | -2.5    |
| 1     | high      | Upper limit of the Z-score                                                              | *null*  |
| 1     | n         | Number of upstream and downstream stations to consider if there is no reference history | 3       |
| 1.1   | low       | Lower limit of the Z-score                                                              | -2      |
| 1.1   | high      | Upper limit of the Z-score                                                              | *null*  |
| 1.1   | n         | Number of upstream and downstream stations to consider for continuity check             | 2       |
| 2     | low       | Lower limit of the Z-score                                                              | -5      |
| 2     | high      | Upper limit of the Z-score                                                              | 5       |
| 2     | n         | Number of upstream and downstream stations to consider if there is no reference history | 4       |

Layer 3 has no adjustable parameters.

### Sequence

The following sequence diagram describes how each job processes ODH data.

![sequence diagram](/pollution_v2/documentation/UML Sequence Diagram.png)

Please note the following, which each job handles itself rather than relying on scheduler-level backfilling.

Due to:
1. ODH limitation (cannot write on ODH a record older than the ones already present),
2. the needing of backfill a new station inserted when the others are already up-to-date,

we have to rely on internal dates management in order to be sure that only the latest unprocessed data is used as input. The information about dates is stored in the checkpoint cache (see [here](#computation-checkpoint)).

1. First the cron schedule starts a new run of the _Validation_ or _Pollution Computation_ job.
2. The job retrieves the station list.
3. For each station the job processes it individually:
   1. it downloads the latest data available,
   2. using the available data, it computes the values,
   3. it uploads the calculated values on ODH.
4. Finally, the job determines if on ODH there is more data to process and, in that case, keeps iterating in the same run until it catches up (see `main.py` of each job for the catch-up loop).

In details, the following steps describe how the pollution computer job works.

1. First the cron schedule starts a new run of the `pollution-computer` job.
2. It first downloads the list of available TrafficSensor stations. A GET request to the `/v2/flat,node/TrafficSensor` endpoint will be used.
3. For each station and lane it will download the latest pollution data available for each class of vehicle class it downloads the last stored measure. Using a GET to the following endpoint `/v2/{representation}/{stationTypes}/{dataTypes}/latest`.
4. Using the available data, the job identifies the new data to download for each lane station and vehicle class.
5. The `TrafficODHConnector` download the new batch of traffic data using the starting point identified in the previous step. Using a GET to the following endpoint `/v2/{representation}/{stationTypes}/{dataTypes}/{from}/{to}`.
6. The `PollutionComputationModel` computes the new PollutionMeasures and returns them to the main task.
7. Finally, the job uploads the new PollutionMeasures to the ODH using the *PollutionODHConnector*.

#### Computation checkpoint

Computation checkpoints are enabled by setting *COMPUTATION_CHECKPOINT_CACHE_PATH* to a SQLite file path (set to an empty string to disable them).

The computation checkpoint stores the final date of the last computed interval of data for a station. The checkpoint is used
as a starting date for the next computation if the station has no pollution data associated.
This feature has been implemented to avoid attempting a recalculation, at each execution of the job, of all
the historical data of the stations that have only invalid data for this library.

Locally (`docker-compose.yml`), the checkpoint file is bind-mounted at `./data/checkpoint_cache.db`. In Kubernetes, it lives
on a PersistentVolumeClaim shared by all jobs, mounted at `/app/data` (see `infrastructure/helm/templates/pvc.yaml`).

By using this cache, computations persist across runs even when errors on the data were found: when a job could not compute
the validation or pollution computation for a station, it updates the checkpoint with the next date to retrieve data and
moves on, rather than blocking the whole run. The next run for that station retrieves the date available from the cache
and continues the computation from there.

## How to maintain it

### Reset checkpoint cache

When a reset is needed (e.g. to make a job process all the data available from the beginning or from a specific date),
delete the checkpoint file.

Locally:
```bash
rm -f ./data/checkpoint_cache.db
```

In Kubernetes, the checkpoint file lives on a PVC shared by all jobs. Release name and namespace are defined in
`.github/workflows/ci-pollution-v2.yml` (`K8S_NAME`, `KUBERNETES_NAMESPACE`), e.g. `el-pollution-v2` in namespace `collector`.

If you have to redo calculations, you must clean the cache:
```bash
kubectl -n collector run checkpoint-cache-cleanup --rm -it --restart=Never \
  --image=busybox \
  --overrides='{"spec":{"containers":[{"name":"cleanup","image":"busybox","command":["sh"],"stdin":true,"tty":true,"volumeMounts":[{"name":"data","mountPath":"/app/data"}]}],"volumes":[{"name":"data","persistentVolumeClaim":{"claimName":"el-pollution-v2-checkpoint-cache"}}]}}' \
  -- sh -c "rm -f /app/data/checkpoint_cache.db"
```

Note: `ODH_MAX_LOOKBACK_DAYS`, if set, caps how far behind a station's start date can be relative to the most-caught-up
station, even with an empty cache.

### Update "parco circolante"

"Parco circolante" stands for the configuration containing the estimate of the distribution of the types of car moving
on the considered road.

The folder `pollution_v2/src/pollution_computer/model/input` contains a dedicated CSV file and copert55.db (a sqlite database) for each year
(e.g. `fc_info_2018.csv`)

When processing data for a specific year, the pollution computer job looks for the file `fc_<year>.csv`: if found, the file is used,
otherwise the system look for the most recent year before `<year>` (e.g. if it does not find 2025 it will try 2024, and so on).  

No configuration needs to be changed, just add the updated file, clean already processed records and let the job run again.

To update the "parco circolante" for a specific year, add the corresponding file and then [reset the checkpoint cache](#reset-checkpoint-cache) for the previously computed data.

Clean previously updated data on Open Data Hub and run the pollution computer job again.

## How to use it

### Setup the project

1. Clone the repository from [here](https://lab.u-hopper.com/u-hopper/projects/industrial/open-data-hub-bz/bdp-elaborations)
2. Move to `pollution_v2` folder
	```commandline
	cd bdp-elaborations/pollution_v2
	```
3. Create a virtual environment and activate it:
	```commandline
	python3 -m venv venv
	source venv/bin/activate
	```
3. Installing the requirements:
	```commandline
	pip install -r requirements.txt
	```
4. For a development environment is suggested to install and configure [pre-commit](https://pre-commit.com/). Pre-commit is a framework for managing and maintaining multi-language pre-commit hooks. The configuration available in this project will run some syntax check before each commit.
	```commandline
	pip install pre-commit
	pre-commit install
	```
5. Copy `.env.example` to `.env` and fill in the ODH credentials and any other setting you need to override.

### Project folders

* `documentation` contains UML diagrams describing the system
* `infrastructure` contains the Dockerfile (`infrastructure/docker/Dockerfile`), the Helm chart (`infrastructure/helm`) and the compose files used for build/test in CI
* `sample_data` contains any sample data useful to test tasks (under .gitignore); sample data for validator are available [here](https://drive.google.com/file/d/1aPFDXOCECvA_h6npYe_aZ0k8vxHTwlYy/view?usp=drive_link)
* `sql` contains maintenance SQL scripts (e.g. deleting elaboration data)
* `dispersal` and `weather` are standalone prediction services (RLine and METRo respectively) called over HTTP by the pollution-dispersal and road-weather jobs; each has its own Dockerfile, requirements and README
* `src` contains source files
  * `src/common` contains shared connectors, data models, managers and the checkpoint cache
  * `src/config` contains configuration files for jobs, e.g. `validator.yaml`, `road_weather.yaml`
  * `src/validator`, `src/pollution_computer`, `src/road_weather`, `src/pollution_dispersal` each contain one job's `main.py` entry point, manager and model
  * `src/tests` contains test files
* `venv`/`.venv` contains Python virtual environment (under .gitignore)

### Running a job locally

Each job can be run once or on a schedule via `docker-compose.yml`:

```bash
# one-shot run, useful for testing
docker compose run --rm validator
docker compose run --rm pollution-computer
docker compose run --rm road-weather
docker compose run --rm pollution-dispersal

# run all jobs continuously, each on its own cron schedule (via supercronic)
docker compose up --detach
```

Cron schedules are set via `VALIDATOR_CRON_SCHEDULE`, `POLLUTION_COMPUTER_CRON_SCHEDULE`, `ROAD_WEATHER_CRON_SCHEDULE`
and `POLLUTION_DISPERSAL_CRON_SCHEDULE` (see `.env.example`); these are only used by `docker-compose.yml` and are
ignored in Kubernetes, where each job's `schedule` is set per-environment in `infrastructure/helm/test.yaml` /
`infrastructure/helm/prod.yaml`.

To run a job directly with Python (e.g. from an IDE run/debug configuration):
1. Set the working directory to `pollution_v2/src` (or add it to `PYTHONPATH`).
2. Set the environment variables listed below (or load them from `.env`).
3. Run the module for the job you want, e.g.:
	```commandline
	python -m validator.main
	python -m pollution_computer.main
	python -m road_weather.main
	python -m pollution_dispersal.main
	```

### Running tests

```bash
cd infrastructure
docker compose -f docker-compose.test.yml build
docker compose -f docker-compose.test.yml run --rm test
```

This is the same command run in CI (see `.github/workflows/ci-pollution-v2.yml`).

#### List of environment variables

| Name                                                   | Required | Description                                                                                                                                                                                                             | Default                                  |
|---------------------------------------------------------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| ODH_BASE_READER_URL                                    | Yes      | The base url for the ODH requests for reading data.                                                                                                                                                                     | -                                         |
| ODH_BASE_WRITER_URL                                    | Yes      | The base url for the ODH requests for writing data.                                                                                                                                                                     | -                                         |
| ODH_AUTHENTICATION_URL                                 | Yes      | The url for ODH authentication endpoints.                                                                                                                                                                               | -                                         |
| ODH_USERNAME                                           | No       | The username for the ODH authentication (only needed for `ODH_GRANT_TYPE=password`).                                                                                                                                   | -                                         |
| ODH_PASSWORD                                           | No       | The password for the ODH authentication (only needed for `ODH_GRANT_TYPE=password`).                                                                                                                                    | -                                         |
| ODH_CLIENT_ID                                          | Yes      | The client ID for the ODH authentication.                                                                                                                                                                               | -                                         |
| ODH_CLIENT_SECRET                                      | Yes      | The client secret for the ODH authentication.                                                                                                                                                                           | -                                         |
| ODH_GRANT_TYPE                                         | No       | The token grant type for the ODH authentication. It is possible to specify more types by separating them using `;`.                                                                                                     | "client_credentials"                      |
| ODH_PAGINATION_SIZE                                    | No       | The pagination size for the get requests to ODH.                                                                                                                                                                        | 5000                                      |
| ODH_MAX_POST_BATCH_SIZE                                | No       | The maximum size of the batch for each post request to ODH. If not present there is not a maximum batch size and all data will sent in a single call.                                                                   | -                                         |
| ODH_PARALLEL_REQUESTS                                  | No       | The number of parallel requests used when downloading traffic data.                                                                                                                                                     | 10                                        |
| ODH_STATIONS_FILTER_ORIGIN                             | No       | Filters the station list to a specific origin, e.g. `A22`.                                                                                                                                                              | -                                         |
| ODH_MINIMUM_STARTING_DATE                              | No       | The minimum starting date[time] in isoformat (up to one second level of precision, milliseconds for the from date field are not supported in ODH) for downloading data from ODH if no measures are available.          | 2018-01-01                                |
| ODH_MAX_LOOKBACK_DAYS                                  | No       | Caps how many days behind the most-caught-up station a lagging station's computation start date can be. Unset disables the cap.                                                                                       | -                                         |
| ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION            | No       | The maximum size (in days) of a batch to compute pollution.                                                                                                                                                             | 30                                        |
| ODH_COMPUTATION_BATCH_SIZE_VALIDATION                  | No       | The maximum size (in days) of a batch to compute validation.                                                                                                                                                            | 1                                         |
| ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL              | No       | The range (in days) used to look for the pollution dispersal computation starting date.                                                                                                                                | 30                                        |
| REQUESTS_TIMEOUT                                       | No       | Timeout (in seconds) for requests to ODH and other HTTP endpoints.                                                                                                                                                      | 300                                       |
| REQUESTS_MAX_RETRIES                                   | No       | Maximum number of retries for failed requests.                                                                                                                                                                          | 1                                         |
| REQUESTS_SLEEP_TIME                                    | No       | Sleep time (in seconds) between requests.                                                                                                                                                                               | 0                                         |
| REQUESTS_RETRY_SLEEP_TIME                              | No       | Sleep time (in seconds) before retrying a failed request.                                                                                                                                                               | 30                                        |
| PROVENANCE_ID                                          | No       | Set if the provenance record already exists in ODH.                                                                                                                                                                     | -                                         |
| PROVENANCE_LINEAGE                                     | No       | The provenance lineage posted to ODH.                                                                                                                                                                                   | "u-hopper"                                |
| PROVENANCE_NAME                                        | No       | The provenance name posted to ODH.                                                                                                                                                                                      | "a22-pollutant-elaboration"               |
| PROVENANCE_VERSION                                     | No       | The provenance version posted to ODH (set to the git SHA in CI).                                                                                                                                                        | "0.1.0"                                   |
| DATATYPE_PREFIX                                        | No       | The prefix for datatypes (both while reading and while creating), useful to test the system simulating nothing has ever been written before on ODH.                                                                     | ""                                        |
| COMPUTATION_CHECKPOINT_CACHE_PATH                      | No       | Path to the SQLite file used for computation checkpoints. Set to an empty string to disable caching entirely.                                                                                                          | "data/checkpoint_cache.db"                |
| VALIDATOR_CONFIG_FILE                                  | No       | The validator config file.                                                                                                                                                                                              | "config/validator.yaml"                   |
| ROAD_WEATHER_CONFIG_FILE                               | No       | The road weather config file.                                                                                                                                                                                           | "config/road_weather.yaml"                |
| METRO_WS_PREDICTION_ENDPOINT                           | No       | The web-service endpoint exposing METRo forecasts.                                                                                                                                                                      | "http://metro:80/predict/?station_code="  |
| ROAD_WEATHER_NUM_FORECASTS                             | No       | The number of forecasts to save on ODH.                                                                                                                                                                                 | 45                                        |
| ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS                 | No       | The minutes between forecasts to be saved on ODH.                                                                                                                                                                       | 60                                        |
| POLLUTION_DISPERSAL_STARTING_DATE                      | No       | The starting date for the pollution dispersal computation.                                                                                                                                                              | "2020-12-01 02:00"                        |
| POLLUTION_DISPERSAL_COMPUTATION_HOURS_SPAN             | No       | The range (in hours) used to download the data to pass to the pollution dispersal model.                                                                                                                               | 1                                         |
| POLLUTION_DISPERSAL_PREDICTION_ENDPOINT                | No       | The web-service endpoint exposing RLine forecasts.                                                                                                                                                                      | "http://rline:80/process/?dt="            |
| POLLUTION_DISPERSAL_STATION_MAPPING_ENDPOINT           | No       | The web-service endpoint exposing RLine capabilities.                                                                                                                                                                   | "http://rline:80/get_capabilities/"       |
| POLLUTION_DISPERSAL_DOMAINS_COORDINATES_REFERENCE_SYSTEM | No     | The coordinates reference system of the stations coordinates returned by the pollution dispersal model.                                                                                                                | 32632                                     |
| DEFAULT_TIMEZONE                                       | No       | Timezone used for scheduling/date computations.                                                                                                                                                                         | "Europe/Rome"                             |
| HISTORY_TIMEZONE                                       | No       | Timezone used when reading history data.                                                                                                                                                                                | "UTC"                                     |
| LOG_LEVEL                                              | No       | Log level for this project's own loggers.                                                                                                                                                                               | "INFO"                                    |
| LOG_LEVEL_LIBS                                         | No       | Log level for third-party libraries.                                                                                                                                                                                    | "WARNING"                                 |
| SENTRY_SAMPLE_RATE                                     | No       | Sentry traces sample rate.                                                                                                                                                                                              | 1.0                                       |
| CRON_SCHEDULE                                          | No       | Cron expression the container runs its command on (via supercronic). If unset, the command runs once and the container exits. Ignored in Kubernetes, where scheduling is done via the CronJob's own `schedule`.        | -                                          |

### Notes on deployment

See the following files:
 * `infrastructure/docker/Dockerfile`: multi-stage image definition (`test` stage for running the test suite, `build` stage with `supercronic` for running jobs)
 * `docker-compose.yml`: one service per job (`validator`, `pollution-computer`, `road-weather`, `pollution-dispersal`), each built from the same image with its own `command` and `CRON_SCHEDULE`; `./data` is bind-mounted to `/app/data` for the checkpoint cache
 * `entrypoint.sh`: if `CRON_SCHEDULE` is set, runs the job's command on that schedule via `supercronic`; otherwise runs the command once
 * `infrastructure/helm`: Helm chart with a single `CronJob` template iterating over the `jobs` map in `values.yaml` (schedule, command and resources are set per job, per environment in `test.yaml`/`prod.yaml`); a shared PVC backs the checkpoint cache for all jobs
 * `.github/workflows/ci-pollution-v2.yml`: CI/CD pipeline — runs tests, lints and validates the Helm chart, builds and pushes the image, then deploys to the `test` environment on push to `main` and to `prod` on push to `prod`

Use the following commands (from the `infrastructure` folder unless noted):
 * `docker compose -f docker-compose.build.yml build`: builds the image
 * `docker compose -f docker-compose.test.yml build && docker compose -f docker-compose.test.yml run --rm test`: runs the test suite
 * `docker compose up --detach` (from the project root): starts all 4 jobs, each on its own cron schedule
 * `docker compose run --rm <job>` (from the project root): runs a single job once
 * `helm lint infrastructure/helm`: lints the chart
 * `helm template el-pollution-v2 infrastructure/helm -f infrastructure/helm/test.yaml`: renders the manifests for the test environment
