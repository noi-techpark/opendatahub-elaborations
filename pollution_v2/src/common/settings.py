# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
from datetime import datetime, timedelta, tzinfo, time

import dateutil.parser
import pytz
from airflow.models import Variable


def get_now(tz: tzinfo | None = None):
    """
    Return now, given timezone. Useful to simulate now different from now.
    """
    return datetime.now(tz)  # - timedelta(days=3)


def get_previous_midnight(tz: tzinfo | None = None):
    """
    Return now, given timezone. Useful to simulate now different from now.
    """
    return datetime.combine((get_now(tz)).date(), time.min)


# Pollution task
POLLUTION_TASK_SCHEDULING_MINUTE = os.getenv("POLLUTION_TASK_SCHEDULING_MINUTE", "*/10")
POLLUTION_TASK_SCHEDULING_HOUR = os.getenv("POLLUTION_TASK_SCHEDULING_HOUR", "*")

# Sentry
SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", 1.0))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_LEVEL_LIBS = os.getenv("LOG_LEVEL_LIBS", "DEBUG")
LOGS_DIR = os.getenv("LOGS_DIR", "")

# General
DEFAULT_TIMEZONE = pytz.timezone(os.getenv("DEFAULT_TIMEZONE", "Europe/Rome"))

# Open Data Hub
ODH_BASE_READER_URL = Variable.get("ODH_BASE_READER_URL")
ODH_BASE_WRITER_URL = Variable.get("ODH_BASE_WRITER_URL")
ODH_AUTHENTICATION_URL = Variable.get("ODH_AUTHENTICATION_URL")
ODH_USERNAME = Variable.get("ODH_USERNAME")
ODH_PASSWORD = Variable.get("ODH_PASSWORD")
ODH_CLIENT_ID = Variable.get("ODH_CLIENT_ID")
ODH_CLIENT_SECRET = Variable.get("ODH_CLIENT_SECRET")
ODH_GRANT_TYPE = Variable.get("ODH_GRANT_TYPE", "password").split(";")
ODH_PAGINATION_SIZE = int(Variable.get("ODH_PAGINATION_SIZE", 200))
ODH_MAX_POST_BATCH_SIZE = int(Variable.get("ODH_MAX_POST_BATCH_SIZE")) if Variable.get("ODH_MAX_POST_BATCH_SIZE") \
    else None
ODH_MINIMUM_STARTING_DATE = dateutil.parser.parse(Variable.get("ODH_MINIMUM_STARTING_DATE", "2018-01-01"))
ODH_MINIMUM_STARTING_DATE = DEFAULT_TIMEZONE.localize(ODH_MINIMUM_STARTING_DATE)
ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION = int(Variable.get("ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION", 30))
ODH_COMPUTATION_BATCH_SIZE_VALIDATION = int(Variable.get("ODH_COMPUTATION_BATCH_SIZE_VALIDATION", 1))
ODH_STATIONS_FILTER_ORIGIN = Variable.get("ODH_STATIONS_FILTER_ORIGIN")

DAG_POLLUTION_EXECUTION_CRONTAB = Variable.get("DAG_POLLUTION_EXECUTION_CRONTAB", "0 2 * * *")
DAG_ROAD_WEATHER_EXECUTION_CRONTAB = Variable.get("DAG_ROAD_WEATHER_EXECUTION_CRONTAB", "0 */3 * * *")
DAG_VALIDATION_EXECUTION_CRONTAB = Variable.get("DAG_VALIDATION_EXECUTION_CRONTAB", "0 0 * * *")
DAG_POLLUTION_DISPERSAL_EXECUTION_CRONTAB = Variable.get("DAG_POLLUTION_DISPERSAL_EXECUTION_CRONTAB", "0 * * * *")
DAG_POLLUTION_TRIGGER_DAG_HOURS_SPAN = int(Variable.get("DAG_POLLUTION_TRIGGER_DAG_HOURS_SPAN", 24))
DAG_VALIDATION_TRIGGER_DAG_HOURS_SPAN = int(Variable.get("DAG_VALIDATION_TRIGGER_DAG_HOURS_SPAN", 24))

PERIOD_10MIN = 600
PERIOD_1HOUR = 3600
PERIOD_1DAY = 86400
PERIOD_1SEC = 1

# Requests management
REQUESTS_TIMEOUT = float(os.getenv("REQUESTS_TIMEOUT", 300))
REQUESTS_MAX_RETRIES = int(os.getenv("REQUESTS_MAX_RETRIES", 1))
REQUESTS_SLEEP_TIME = float(os.getenv("REQUESTS_SLEEP_TIME", 0))
REQUESTS_RETRY_SLEEP_TIME = float(os.getenv("REQUESTS_RETRY_SLEEP_TIME", 30))

# Provenance
PROVENANCE_ID = os.getenv("PROVENANCE_ID")
PROVENANCE_LINEAGE = os.getenv("PROVENANCE_LINEAGE", "u-hopper")
PROVENANCE_NAME = os.getenv("PROVENANCE_NAME", "a22-pollutant-elaboration")
PROVENANCE_NAME_POLL_ELABORATION = os.getenv("PROVENANCE_NAME_POLL_ELABORATION", PROVENANCE_NAME)
PROVENANCE_NAME_VALIDATION = os.getenv("PROVENANCE_NAME_VALIDATION", PROVENANCE_NAME)
PROVENANCE_VERSION = os.getenv("PROVENANCE_VERSION", "0.1.0")

COMPUTATION_CHECKPOINT_REDIS_HOST = Variable.get("COMPUTATION_CHECKPOINT_REDIS_HOST", None)
COMPUTATION_CHECKPOINT_REDIS_PORT = int(Variable.get("COMPUTATION_CHECKPOINT_REDIS_PORT", 6379))
COMPUTATION_CHECKPOINT_REDIS_DB = int(Variable.get("COMPUTATION_CHECKPOINT_REDIS_DB", 0))

AIRFLOW_NUM_RETRIES = 3

# use it not empty to add a test prefix to datatype
DATATYPE_PREFIX = Variable.get("DATATYPE_PREFIX", "")

VALIDATOR_CONFIG_FILE = Variable.get("VALIDATOR_CONFIG_FILE", "config/validator.yaml")

MAIN_DIR = os.getenv("MAIN_DIR", ".")
TMP_DIR = f'{MAIN_DIR}/tmp'
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

ROAD_WEATHER_CONFIG_FILE = Variable.get("ROAD_WEATHER_CONFIG_FILE", "config/road_weather.yaml")
METRO_WS_PREDICTION_ENDPOINT = Variable.get("METRO_WS_PREDICTION_ENDPOINT", "http://metro:80/predict/?station_code=")
ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS = int(Variable.get("ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS", 60))
ROAD_WEATHER_NUM_FORECASTS = int(Variable.get("ROAD_WEATHER_NUM_FORECASTS", 45))

# - Pollution dispersal algorithm computes data in a one-hour period from the starting date
# Days batch size for pollution dispersal is used to check available data during the computation of the starting date
# We need a batch size in multiple days (instead of one hour) to speed up the look-up of the starting date and to avoid
#    a case where there is an hour gap in all the data (every year on 31/12 at 23.00)
ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL = int(Variable.get("ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL", 30))
# After a computation is completed, look in the next hours for new data to trigger a new computation
DAG_POLLUTION_DISPERSAL_TRIGGER_DAG_HOURS_SPAN = int(Variable.get("DAG_POLLUTION_DISPERSAL_TRIGGER_DAG_HOURS_SPAN", 24))
POLLUTION_DISPERSAL_COMPUTATION_HOURS_SPAN = int(Variable.get("POLLUTION_DISPERSAL_COMPUTATION_HOURS_SPAN", 1))
POLLUTION_DISPERSAL_STARTING_DATE = dateutil.parser.parse(Variable.get("POLLUTION_DISPERSAL_STARTING_DATE",
                                                                       "2020-12-01 02:00"))
POLLUTION_DISPERSAL_PREDICTION_ENDPOINT = Variable.get("POLLUTION_DISPERSAL_PREDICTION_ENDPOINT",
                                                       "http://rline:80/process/?dt=")
POLLUTION_DISPERSAL_STATION_MAPPING_ENDPOINT = Variable.get("POLLUTION_DISPERSAL_STATION_MAPPING_ENDPOINT",
                                                            "http://rline:80/get_capabilities/")
POLLUTION_DISPERSAL_DOMAINS_COORDINATES_REFERENCE_SYSTEM = Variable.get(
    "POLLUTION_DISPERSAL_DOMAINS_COORDINATES_REFERENCE_SYSTEM", "32632")
