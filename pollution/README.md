# Pollution connector


This project contain the code for the PollutionConnect for the OpenDataHub.

The TrafficData is periodically pulled from the A22 collection and the pollution data is estimate and pushed back on the OpenDataHub.

## Project Structure

![project structure](/pollution/documentation/Architecture.png)


**Components**:

- *Scheduler*: It schedules the periodic task to update the pollution data.
- *Pollution Computation Task*: This task handles the computation of a batch of measures. It downloads the traffic data from the OpenDataHub (Using the TrafficMeasure connector), computes the pollution measures (using the Pollution Computation Model) and it uploads the new measure to the ODH using the PollutionMeasure connector.
- *TrafficODHConnector*: This component downloads and parse the traffic data from the ODH.
- *PollutionODHConnector*: This component handles the upload and the download of the Pollution Measures from the ODH.
- *PollutionComputationModel*: This component computes new PollutionMeasure from the input TrafficMeasures.

### Batch computation sequence

![sequence diagram](/pollution/documentation/SequenceDiagram.png)

1. First the scheduler starts the execution of a new `Pollution Computation Task`.
2. Then the task will first, download the list of available TrafficSensor stations. A GET request to the `/v2/flat,node/TrafficSensor` endpoint will be used.
3. For each station and lane it will download the latest pollution data available for each class of vehicle class it downloads the last stored measure. Using a GET to the following endpoint `/v2/{representation}/{stationTypes}/{dataTypes}/latest`.
4. Using the available data, the `Pollution Computation Task` identifies the new data to download for each lane station and vehicle class.
5. The `TrafficODHConnector` download the new batch of traffic data using the starting point identified in the previous step. Using a GET to the following endpoint `/v2/{representation}/{stationTypes}/{dataTypes}/{from}/{to}`.
6. The `PollutionComputationModel` computes the new PollutionMeasures and returns them to the main task.
7. Finally, the main task uploads the new PollutionMeasures to the ODH using the *PollutionODHConnector*.

## How to use it

### Setup The project

1. Clone the repository
2. Create a virtual environment and activate it:

```commandline
python3 -m venv venv
source .venv/bin/activate
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

### Run in production mode

First setup the project and then

1. Start a local instance of redis and then export the required environmental variables:
```commandline
export CELERY_BACKEND_URL=redis://<redis-host>:<redis-port>/<target-db>
export CELERY_BROKER_URL=redis://<redis-host>:<redis-port>/<target-db>
```

2. Run the celery worker:
```commandline
celery -A pollution_connector.celery_configuration.celery_app worker --loglevel=INFO
```

3. Run the celery beat scheduler:
```commandline
celery -A pollution_connector.celery_configuration.celery_app beat --loglevel=INFO
```

### Run a single task

For a development environment or a one-off run of the pollution computation is possible to execute a single run of the pollution computation.

First setup the project and then run the following:

```commandline
cd src
python -m pollution_connector.main
```

For the available configurations type:
```commandline
cd src
python -m pollution_connector.main -h
```

### List of environmental variables

| Name                             | Required | Description                                                                                                                                                                                                             | Default                       |
|----------------------------------|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| CELERY_BROKER_URL                | Yes      | The url of the celery broker.                                                                                                                                                                                           | -                             |
| CELERY_BACKEND_URL               | Yes      | The url of the celery result backend.                                                                                                                                                                                   | -                             |
| CELERY_RESULT_EXPIRATION_SECONDS | Yes      | The expiration time (in seconds) of the celery results.                                                                                                                                                                 | 604800 (one week)             |
| POLLUTION_TASK_SCHEDULING_MINUTE | No       | The minutes on which the pollution computation task is schedule. See below for further details.                                                                                                                         | */10 (runs every ten minutes) |
| POLLUTION_TASK_SCHEDULING_HOUR   | No       | The hours on which the pollution computation task is schedule. See below for further details.                                                                                                                           | *                             |
| SENTRY_DSN                       | No       | The data source name for sentry, if not set the project will not create any event.                                                                                                                                      | -                             |
| SENTRY_RELEASE                   | No       | If set, sentry will associate the events to the given release.                                                                                                                                                          | -                             |
| SENTRY_ENVIRONMENT               | No       | If set, sentry will associate the events to the given environment (ex. `production`, `staging`).                                                                                                                        | -                             |
| SENTRY_SAMPLE_RATE               | No       | The sample rate for the transactions that will be logged in sentry (1.0=all, 0.0=none). Default to `1.0`.                                                                                                               | -                             |
| LOG_LEVEL                        | No       | The logging level of the project.                                                                                                                                                                                       | INFO                          |
| LOG_LEVEL_LIBS                   | No       | The logging level of the libraries.                                                                                                                                                                                     | DEBUG                         |
| LOG_TO_FILE                      | No       | Log to file if this variable is present.                                                                                                                                                                                | -                             |
| LOGS_DIR                         | No       | The directory where to store the log file.                                                                                                                                                                              | "" (empty string)             |
| ODH_BASE_READER_URL              | Yes      | The base url for the ODH requests for reading data.                                                                                                                                                                     | -                             |
| ODH_BASE_WRITER_URL              | Yes      | The base url for the ODH requests for writing data.                                                                                                                                                                     | -                             |
| ODH_AUTHENTICATION_URL           | Yes      | The url for ODH authentication endpoints.                                                                                                                                                                               | -                             |
| ODH_USERNAME                     | Yes      | The username for the ODH authentication.                                                                                                                                                                                | -                             |
| ODH_PASSWORD                     | Yes      | The password for the ODH authentication.                                                                                                                                                                                | -                             |
| ODH_CLIENT_ID                    | Yes      | The client ID for the ODH authentication.                                                                                                                                                                               | -                             |
| ODH_CLIENT_SECRET                | Yes      | The client secret for the ODH authentication.                                                                                                                                                                           | -                             |
| ODH_GRANT_TYPE                   | Yes      | The token grant type for the ODH authentication. It is possible to specify more types by separating them using `;`.                                                                                                     | "password"                    |
| ODH_PAGINATION_SIZE              | No       | The pagination size for the get requests to ODH. Set it to `-1` to disable it.                                                                                                                                          | 200                           |
| ODH_MAX_POST_BATCH_SIZE          | No       | The maximum size of the batch for each post request to ODH. If not present there is not a maximum batch size and all data will sent in a single call.                                                                   | -                             |
| ODH_MINIMUM_STARTING_DATE        | No       | The minimum starting date[time] in isoformat (up to one second level of precision, milliseconds for the from date field are not supported in ODH) for downloading data from ODH if no pollution measures are available. | 2018-01-01                    |
| DEFAULT_TIMEZONE                 | No       | The default timezone for parsing datetimes if no one is present.                                                                                                                                                        | Europe/Rome                   |
| REQUESTS_TIMEOUT                 | No       | The timeout for the requests (expressed in seconds).                                                                                                                                                                    | 300                           |
| REQUESTS_MAX_RETRIES             | No       | The maximum number of retries for the requests.                                                                                                                                                                         | 1                             |
| REQUESTS_SLEEP_TIME              | No       | The sleep time between the requests when getting paginated data (expressed in seconds).                                                                                                                                 | 0                             |
| REQUESTS_RETRY_SLEEP_TIME        | No       | The sleep time between retries for the requests (expressed in seconds).                                                                                                                                                 | 30                            |
| PROVENANCE_ID                    | No       | The id of the provenance.                                                                                                                                                                                               | -                             |
| PROVENANCE_LINEAGE               | No       | The lineage of the provenance.                                                                                                                                                                                          | u-hopper                      |
| PROVENANCE_NAME                  | No       | The name of the data collector of the provenance.                                                                                                                                                                       | a22-pollutant-elaboration     |
| PROVENANCE_VERSION               | No       | The version of the data collector of the provenance.                                                                                                                                                                    | 0.1.0                         |

* *POLLUTION_TASK_SCHEDULING_MINUTE*: This variable represents the minutes on which the pollution computation task is scheduled. It uses the crontab syntax so the following are valid:
  * `*` runs every minute;
  * `2` runs on the second minute;
  * `*/10` runs every 10 minutes.

* *POLLUTION_TASK_SCHEDULING_HOUR*: This variable represents the hour on which the pollution computation task is scheduled. It uses the crontab syntax so the following are valid:
  * `*` runs every hour;
  * `3` runs at 3 AM;
  * `*/2` runs every 2 hours.
