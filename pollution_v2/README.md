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

- *Airflow*: It schedules the periodic task to update the validation and the pollution data.
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

The following sequence diagram describes how Airflow and the DAGs (validation or pollution computing) interact in order to process ODH data.

![sequence diagram](/pollution_v2/documentation/UML Sequence Diagram.png)

Please note the following, apparently contrasting with Airflow capabilities of scheduling
DAGs in backfill mode.

Due to:
1. ODH limitation (cannot write on ODH a record older than the ones already present),
2. the needing of backfill a new station inserted when the others are already up-to-date,

we have to rely on internal dates management in order to be sure that only the latest unprocessed data is used as DAG input. The information about dates is stored in the Redis container available on docker compose configuration (see [here](#computation-checkpoint)).

1. First the scheduler starts the execution of a new _Validation_ or _Pollution Computation_ DAG.
2. Then the DAG activates the first task that retrieves the station list.
3. For each station the DAG runs a task in charge of process the single station:
   1. the task will download the latest data available,
   2. using the available data, the task computes the values,
   3. the task uploads the calculated values on ODH.
4. Finally, the DAG determine if on ODH there are more data to process and, in that case, triggers another DAG run to process them.

In details, the following step describe how the pollution computation DAG works.

1. First the scheduler starts the execution of a new `Pollution Computation DAG`.
2. Then the task will first, download the list of available TrafficSensor stations. A GET request to the `/v2/flat,node/TrafficSensor` endpoint will be used.
3. For each station and lane it will download the latest pollution data available for each class of vehicle class it downloads the last stored measure. Using a GET to the following endpoint `/v2/{representation}/{stationTypes}/{dataTypes}/latest`.
4. Using the available data, the `Pollution Computation DAG` identifies the new data to download for each lane station and vehicle class.
5. The `TrafficODHConnector` download the new batch of traffic data using the starting point identified in the previous step. Using a GET to the following endpoint `/v2/{representation}/{stationTypes}/{dataTypes}/{from}/{to}`.
6. The `PollutionComputationModel` computes the new PollutionMeasures and returns them to the main task.
7. Finally, the main task uploads the new PollutionMeasures to the ODH using the *PollutionODHConnector*.

#### Computation checkpoint
By setting the *COMPUTATION_CHECKPOINT_REDIS_HOST* variable to a valid Redis server, the computation checkpoints will be enabled.

The computation checkpoint stores the final date of the last computed interval of data for a station. The checkpoint is used
as a starting date for the next computation if the station has no pollution data associated.
This feature has been implemented to avoid attempting a recalculation, at each execution of the task, of all
the historical data of the stations that have only invalid data for this library.

We can use the Redis host made available by airflow when building its containers. The environment variable
(taken from `docker-compose.yaml`) dictating the redis host used by airflow is:

```
AIRFLOW__CELERY__BROKER_URL: redis://:@redis:6379/0
```

This is standard for Airflow and means it connects to Redis host at port 6379, with database 0.
Redis supports up to 16 databases, and they are independent from each other.
Therefore we can use the redis host already present to check for the computation error, we just need to use a different database.
We can use these environment variables (db is set to 10, but needs only to be different from 0):

```
AIRFLOW_VAR_COMPUTATION_CHECKPOINT_REDIS_HOST: 'redis'
AIRFLOW_VAR_COMPUTATION_CHECKPOINT_REDIS_PORT: 6379
AIRFLOW_VAR_COMPUTATION_CHECKPOINT_REDIS_DB: 10
```

By using these settings, the computations persist when errors on the data were found.
When a task could not compute the validation or pollution computation, it updated the redis cache with the next
date to retrieve data and then finished with MARK=SUCCESS, thus not breaking the flow of task executions.
The next planned task for that station retrieves the date available from cache and continues the computation from there.

## How to maintain it

### Reset Airflow Redis cache

When a reset of the workflow manager is needed (e.g. to make it process all the data available from the beginning or
from a specific date), you need to clean the Redis volume used as state database as detailed above. Once
stopped the docker compose, remove the dedicated volume and start again the compose or cleanup keys as follows.

Connect to the container
```bash
docker exec -it {{container_name}} bash
```

Clean Redis db
```bash
redis-cli -n 10 flushdb
```

Check there are no keys
```bash
redis-cli -n 10 keys '*'
```

Look for a specific key
```bash
redis-cli -n 10 GET "ComputationCheckpoint-A22:6127:4-VALIDATION"
redis-cli -n 10 KEYS '*POLLUTION*'
```

Delete a specific key
```bash
redis-cli -n 10 KEYS '*POLLUTION*' | xargs -r redis-cli -n 10 DEL
```

### Update "parco circolante"

"Parco circolante" stands for the configuration containing the estimate of the distribution of the types of car moving
on the considered road.

The folder `pollution_v2/src/pollution_connector/model/input` contains a dedicated CSV file for each year
(e.g. `fc_info_2018.csv`) with a default one containing default values in case of processing a year with the
corresponding file missing (`fc_info.csv`).

When processing data for a specific year, the DAG looks for the file `fc_<year>.csv`: if found, the file is used,
otherwise the system will use the default file `fc.csv` (e.g. with files `fc_2022.csv`, `fc_2023.csv` and `fc.csv`,
when processing data for the year 2023 the system will use `fc_2023.csv` and when processing data for 2020 and/or 2024
the system will use `fc.csv`. No configuration needs to be changed, just add the updated file, clean already
processed records and let the DAGs run.

To update the "parco circolante" for a specific year, just add the corresponding file (and update the default file, if
appropriate) and then [reset the Airflow cache](#Reset-Airflow-Redis-cache) for the previously computed data.

Clean previously updated data on ODH and run again the corresponding DAGs.

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

### Project folders

* ```airflow``` contains Airflow installation files (under .gitignore)
* ```documentation``` contains UML diagrams describing the system
* ```sample_data``` contains any sample data useful to test tasks (under .gitignore); sample data for validator are available [here](https://drive.google.com/file/d/1aPFDXOCECvA_h6npYe_aZ0k8vxHTwlYy/view?usp=drive_link)
* ```src```contains source files
  * ```src/config``` contains configuration files for tasks, e.g. validator
  * ```src/dags```contains DAG of the project
  * ```src/tests``` contains test files
* ```venv``` contains Python virtual environment (under .gitignore)

### Setup Airflow

1. Move to project folder (.)
2. Set Airflow Home
```commandline
mkdir ./airflow
export AIRFLOW_HOME=<your_local_path>/pollution_v2/airflow
```
3. Install Airflow running the following commands
```commandline
AIRFLOW_VERSION=2.8.1
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```
4. If needed (see console errors on first run, see below), install the following:
```commandline
pip install apache-airflow-providers-cncf-kubernetes
```
5. Run Airflow Standalone
```commandline
airflow standalone
```
6. Test it by accessing the Airflow UI: http://localhost:8080 and check files creation in ```./airflow``` (at least ```airflow.cfg```)
7. Trigger a few task instances (optional)
```commandline
# run your first task instance
airflow tasks test example_bash_operator runme_0 2015-01-01
```
```commandline
# backfill: when you may want to run the DAG for a specified historical period even when catchup is disabled, e.g. before the start_date
airflow dags backfill example_bash_operator --start-date 2015-01-01 --end-date 2015-01-02

# clear: after task failure, once errors have been fixed, you can re-run the tasks by clearing them for the scheduled date
airflow dags backfill example_bash_operator --start-date 2015-01-01 --end-date 2015-01-02
```
8. More commands (optional)

Run scheduler alone
```commandline
airflow scheduler
```
Run webserver alone
```commandline
airflow webserver
```
9. Once Airflow is running on samples, change DAG folder in file ```./airflow/airflow.cfg```
```commandline
dags_folder = <your_local_path>/pollution_v2/src
```
9. Once Airflow is running on samples, change DAG folder in file ```./airflow/airflow.cfg``` and skip examples loading
```commandline
dags_folder = <your_local_path>/pollution_v2/src
load_examples = False
```

### Working with DAGs

1. Check DAG consistency over Python
```commandline
python ./src/dags/<name>.py
```
```commandline
# if errors in importing modules, try adding src folder to PYTHONPATH
# see https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html
export PYTHONPATH=<your_local_path>/pollution_v2/src
```
2. Check DAG code processing time
```commandline
time python ./airflow/dags/<name>.py
```
3. List available DAGs
```commandline
airflow dags list
```
4. Test DAG run
```commandline
airflow dags test pollution_computer
airflow dags test pollution_computer 2024-01-01
```

### Working on Tasks

1. List tasks in DAG
```commandline
airflow tasks list tutorial_of_mines
airflow tasks list tutorial_of_mines --tree
```
2. Test single task from DAG
```commandline
airflow tasks test tutorial_of_mines print_date 2015-06-01
```

### Resources
[Airflow best practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)

### Run/debug configuration

1. Create a Python run/debug configuration named 'airflow standalone' or similar.
2. Select 'module' on drop-down list and fill the next field with 'airflow'.
3. Specify as Working directory the following: '<your_local_path>/pollution_v2'.
4. Set the following environmental variables.

#### List of environmental variables for development

| Name                                                                 | Required       | Description                                                                                                                                                                                                             | Default                                  |
|----------------------------------------------------------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| AIRFLOW_HOME                                                         | Yes            | Airflow home.                                                                                                                                                                                                           | -                                        |
| AIRFLOW_VAR_ODH_BASE_READER_URL                                      | Yes            | The base url for the ODH requests for reading data.                                                                                                                                                                     | -                                        |
| AIRFLOW_VAR_ODH_BASE_WRITER_URL                                      | Yes            | The base url for the ODH requests for writing data.                                                                                                                                                                     | -                                        |
| AIRFLOW_VAR_ODH_AUTHENTICATION_URL                                   | Yes            | The url for ODH authentication endpoints.                                                                                                                                                                               | -                                        |
| AIRFLOW_VAR_ODH_USERNAME                                             | Yes            | The username for the ODH authentication.                                                                                                                                                                                | -                                        |
| AIRFLOW_VAR_ODH_PASSWORD                                             | Yes            | The password for the ODH authentication.                                                                                                                                                                                | -                                        |
| AIRFLOW_VAR_ODH_CLIENT_ID                                            | Yes            | The client ID for the ODH authentication.                                                                                                                                                                               | -                                        |
| AIRFLOW_VAR_ODH_CLIENT_SECRET                                        | Yes            | The client secret for the ODH authentication.                                                                                                                                                                           | -                                        |
| AIRFLOW_VAR_ODH_GRANT_TYPE                                           | Yes            | The token grant type for the ODH authentication. It is possible to specify more types by separating them using `;`.                                                                                                     | "password"                               |
| AIRFLOW_VAR_ODH_PAGINATION_SIZE                                      | No             | The pagination size for the get requests to ODH. Set it to `-1` to disable it.                                                                                                                                          | 200                                      |
| AIRFLOW_VAR_ODH_MAX_POST_BATCH_SIZE                                  | No             | The maximum size of the batch for each post request to ODH. If not present there is not a maximum batch size and all data will sent in a single call.                                                                   | -                                        |
| AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION              | No             | The maximum size (in days) of a batch to compute pollution                                                                                                                                                              | 30                                       |
| AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_VALIDATION                    | No             | The maximum size (in days) of a batch to compute validation                                                                                                                                                             | 1                                        |
| AIRFLOW_VAR_ODH_MINIMUM_STARTING_DATE                                | No             | The minimum starting date[time] in isoformat (up to one second level of precision, milliseconds for the from date field are not supported in ODH) for downloading data from ODH if no pollution measures are available. | 2018-01-01                               |
| AIRFLOW_VAR_DATATYPE_PREFIX                                          | No             | The prefix for datatypes (both while reading and while creating), useful to test the system simulating nothing has ever been written before on ODH.                                                                     |                                          |
| COMPUTATION_CHECKPOINT_REDIS_HOST                                    | No             | The redis host for the computation checkpoints. Set to enable the computation checkpoints                                                                                                                               |                                          |
| COMPUTATION_CHECKPOINT_REDIS_PORT                                    | No             | The port for the redis server for the computation checkpoints                                                                                                                                                           | 6379                                     |
| COMPUTATION_CHECKPOINT_REDIS_DB                                      | No             | The DB number of the checkpoint redis server                                                                                                                                                                            | 0                                        |
| AIRFLOW_VAR_DAG_POLLUTION_EXECUTION_CRONTAB                          | No             | The crontab used to schedule pollution computation                                                                                                                                                                      | 0 0 * * *                                |
| AIRFLOW_VAR_DAG_VALIDATION_EXECUTION_CRONTAB                         | No             | The crontab used to schedule data validation                                                                                                                                                                            | 0 0 * * *                                |
| AIRFLOW_VAR_DAG_ROAD_WEATHER_EXECUTION_CRONTAB                       | No             | The crontab used to schedule data road weather conditions calculation                                                                                                                                                   | 0 */3 * * *                              |
| AIRFLOW_VAR_VALIDATOR_CONFIG_FILE                                    | No             | The validator config file                                                                                                                                                                                               | "src/config/validator.yaml"              |
| AIRFLOW_VAR_ROAD_WEATHER_CONFIG_FILE                                 | No             | The road weather config file                                                                                                                                                                                            | "config/road_weather.yaml"               |
| AIRFLOW_VAR_METRO_WS_PREDICTION_ENDPOINT                             | No             | The web-service endpoint exposing METRo forecasts                                                                                                                                                                       | "http://metro:80/predict/?station_code=" |
| AIRFLOW_VAR_ROAD_WEATHER_NUM_FORECASTS                               | No             | The number of forecasts to save on ODH                                                                                                                                                                                  | 48                                       |
| AIRFLOW_VAR_ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS                   | No             | The minutes between forecasts to be saved on ODH                                                                                                                                                                        | 60                                       |
| AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL                | No             | The range (in days) used to look for the computation starting date.                                                                                                                                                     | 30                                       |
| AIRFLOW_VAR_DAG_POLLUTION_DISPERSAL_TRIGGER_DAG_HOURS_SPAN           | No             | After a computation is completed, look in the next hours for new data to trigger a new computation.                                                                                                                     | 24                                       |
| AIRFLOW_VAR_POLLUTION_DISPERSAL_STARTING_DATE                        | No             | The starting date for the pollution dispersal computation.                                                                                                                                                              | "2020-12-01 02:00"                       |
| AIRFLOW_VAR_POLLUTION_DISPERSAL_COMPUTATION_HOURS_SPAN               | No             | The range (in hours) used to download the data to pass to the pollution dispersal model.                                                                                                                                | 1                                        |
| AIRFLOW_VAR_POLLUTION_DISPERSAL_PREDICTION_ENDPOINT                  | No             | The web-service endpoint exposing RLine forecasts                                                                                                                                                                       | "http://rline:80/process/?dt="           |
| AIRFLOW_VAR_POLLUTION_DISPERSAL_STATION_MAPPING_ENDPOINT             | No             | The web-service endpoint exposing RLine capabilities                                                                                                                                                                    | "http://rline:80/get_capabilities/       |
| AIRFLOW_VAR_POLLUTION_DISPERSAL_DOMAINS_COORDINATES_REFERENCE_SYSTEM | No             | The coordinates reference system of the stations coordinates returned by the pollution dispersal model.                                                                                                                 | 32632                                    |
| AIRFLOW_CONN_MINIO_S3_CONN                                           | No             | The MinIO connetion parameters (if expressed as JSON it could be necessary to escape double quotes)                                                                                                                     |                                          |
| AIRFLOW__CORE__REMOTE_LOGGING                                        | No             | The flag enabling remote logging (install `pip install apache-airflow-providers-amazon` if not present)                                                                                                                 |                                          |
| AIRFLOW__CORE__REMOTE_BASE_LOG_FOLDER                                | No             | The bucket name for remote logging                                                                                                                                                                                      |                                          |
| AIRFLOW__CORE__REMOTE_LOG_CONN_ID                                    | No             | The remote logging connection id                                                                                                                                                                                        |                                          |
| AIRFLOW__CORE__ENCRYPT_S3_LOGS                                       | No             | The flag for remote logs encryption                                                                                                                                                                                     |                                          |
| AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG                              | No             | The maximun number of active tasks (running in parallel) for each executing DAG                                                                                                                                         | 16                                       |
| NO_PROXY                                                             | Yes (on macOS) | Sets every URL to skip proxy (see [here](https://docs.python.org/3/library/urllib.request.html))                                                                                                                        | -                                        |                                                                                                                                                                                                   |

### Notes on Docker deployment

[Main reference](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)

[Useful reference](https://copyprogramming.com/howto/how-to-install-packages-in-airflow-docker-compose)

See the following files:
 * `Dockerfile`: definition of custom image with correct image reference and requirements installation instructions
 * `docker-compose.yaml`: service definitions:
     * `airflow-scheduler` - the scheduler monitors all tasks and DAGs, then triggers the task instances once their dependencies are complete
     * `airflow-webserver` - the webserver is available at http://localhost:8080
     * `airflow-worker` - the worker that executes the tasks given by the scheduler
     * `airflow-triggerer` - the triggerer runs an event loop for deferrable tasks
     * `airflow-init` - the initialization service
     * `postgres` - the database
     * `redis` - the redis - broker that forwards messages from scheduler to worker.
* `airflow.sh`: optional wrapper scripts that will allow you to run commands with a simpler command

Use the following commands (could be necessary to use `docker-compose` on older Docker Compose versions):
 * `docker compose up airflow-init`: runs database migrations and create the first user account
 * `docker compose up`: starts all services
 * `docker compose up --detach`: starts all services in detached mode
 * `docker compose --profile flower up`: starts all services plus the flower app for monitoring the environment
 * `docker compose down --volumes --remove-orphans`: cleans-up the environment
 * `docker compose down --volumes --rmi all`: stops and deletes containers, deletes volumes with database data and downloads images

