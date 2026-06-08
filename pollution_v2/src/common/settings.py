# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
from datetime import datetime, time, timedelta, tzinfo
from typing import Optional

import dateutil.parser
import pytz


def get_now(tz: Optional[tzinfo] = None) -> datetime:
    return datetime.now(tz)


def get_previous_midnight(tz: Optional[tzinfo] = None) -> datetime:
    return datetime.combine(get_now(tz).date(), time.min)


# Sentry
SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_LEVEL_LIBS = os.getenv("LOG_LEVEL_LIBS", "WARNING")

# General
DEFAULT_TIMEZONE = pytz.timezone(os.getenv("DEFAULT_TIMEZONE", "Europe/Rome"))
HISTORY_TIMEZONE = pytz.timezone(os.getenv("HISTORY_TIMEZONE", "UTC"))

# Open Data Hub
ODH_BASE_READER_URL = os.getenv("ODH_BASE_READER_URL")
ODH_BASE_WRITER_URL = os.getenv("ODH_BASE_WRITER_URL")
ODH_AUTHENTICATION_URL = os.getenv("ODH_AUTHENTICATION_URL")
ODH_USERNAME = os.getenv("ODH_USERNAME")
ODH_PASSWORD = os.getenv("ODH_PASSWORD")
ODH_CLIENT_ID = os.getenv("ODH_CLIENT_ID")
ODH_CLIENT_SECRET = os.getenv("ODH_CLIENT_SECRET")
ODH_GRANT_TYPE = os.getenv("ODH_GRANT_TYPE", "client_credentials").split(";")
ODH_PAGINATION_SIZE = int(os.getenv("ODH_PAGINATION_SIZE", "200"))
_max_post = os.getenv("ODH_MAX_POST_BATCH_SIZE")
ODH_MAX_POST_BATCH_SIZE = int(_max_post) if _max_post else None
ODH_MINIMUM_STARTING_DATE = DEFAULT_TIMEZONE.localize(
    dateutil.parser.parse(os.getenv("ODH_MINIMUM_STARTING_DATE", "2018-01-01"))
)
ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION = int(os.getenv("ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION", "30"))
ODH_COMPUTATION_BATCH_SIZE_VALIDATION = int(os.getenv("ODH_COMPUTATION_BATCH_SIZE_VALIDATION", "1"))
ODH_STATIONS_FILTER_ORIGIN = os.getenv("ODH_STATIONS_FILTER_ORIGIN")

# Requests
REQUESTS_TIMEOUT = float(os.getenv("REQUESTS_TIMEOUT", "300"))
REQUESTS_MAX_RETRIES = int(os.getenv("REQUESTS_MAX_RETRIES", "1"))
REQUESTS_SLEEP_TIME = float(os.getenv("REQUESTS_SLEEP_TIME", "0"))
REQUESTS_RETRY_SLEEP_TIME = float(os.getenv("REQUESTS_RETRY_SLEEP_TIME", "30"))

# Provenance
PROVENANCE_ID = os.getenv("PROVENANCE_ID")
PROVENANCE_LINEAGE = os.getenv("PROVENANCE_LINEAGE", "u-hopper")
PROVENANCE_NAME = os.getenv("PROVENANCE_NAME", "a22-pollutant-elaboration")
PROVENANCE_NAME_POLL_ELABORATION = os.getenv("PROVENANCE_NAME_POLL_ELABORATION", PROVENANCE_NAME)
PROVENANCE_NAME_VALIDATION = os.getenv("PROVENANCE_NAME_VALIDATION", PROVENANCE_NAME)
PROVENANCE_VERSION = os.getenv("PROVENANCE_VERSION", "0.1.0")

# Checkpoint cache (SQLite file — delete to reset, or set to empty string to disable)
COMPUTATION_CHECKPOINT_CACHE_PATH = os.getenv("COMPUTATION_CHECKPOINT_CACHE_PATH", "data/checkpoint_cache.db")

# Dry-run mode — log writes instead of sending them to ODH. Safe for local testing.
ODH_DRY_RUN = os.getenv("ODH_DRY_RUN", "false").lower() == "true"

# Optional prefix for data type names (e.g. for test environments)
DATATYPE_PREFIX = os.getenv("DATATYPE_PREFIX", "")

# Config file paths
VALIDATOR_CONFIG_FILE = os.getenv("VALIDATOR_CONFIG_FILE", "config/validator.yaml")
ROAD_WEATHER_CONFIG_FILE = os.getenv("ROAD_WEATHER_CONFIG_FILE", "config/road_weather.yaml")

# Temporary working directory
MAIN_DIR = os.getenv("MAIN_DIR", ".")
TMP_DIR = f"{MAIN_DIR}/tmp"
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

# Road weather
METRO_WS_PREDICTION_ENDPOINT = os.getenv("METRO_WS_PREDICTION_ENDPOINT", "http://metro:80/predict/?station_code=")
ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS = int(os.getenv("ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS", "60"))
ROAD_WEATHER_NUM_FORECASTS = int(os.getenv("ROAD_WEATHER_NUM_FORECASTS", "45"))

# Pollution dispersal
ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL = int(os.getenv("ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL", "30"))
POLLUTION_DISPERSAL_COMPUTATION_HOURS_SPAN = int(os.getenv("POLLUTION_DISPERSAL_COMPUTATION_HOURS_SPAN", "1"))
POLLUTION_DISPERSAL_STARTING_DATE = dateutil.parser.parse(
    os.getenv("POLLUTION_DISPERSAL_STARTING_DATE", "2020-12-01 02:00")
)
POLLUTION_DISPERSAL_PREDICTION_ENDPOINT = os.getenv(
    "POLLUTION_DISPERSAL_PREDICTION_ENDPOINT", "http://rline:80/process/?dt="
)
POLLUTION_DISPERSAL_STATION_MAPPING_ENDPOINT = os.getenv(
    "POLLUTION_DISPERSAL_STATION_MAPPING_ENDPOINT", "http://rline:80/get_capabilities/"
)
POLLUTION_DISPERSAL_DOMAINS_COORDINATES_REFERENCE_SYSTEM = os.getenv(
    "POLLUTION_DISPERSAL_DOMAINS_COORDINATES_REFERENCE_SYSTEM", "32632"
)

PERIOD_10MIN = 600
PERIOD_1HOUR = 3600
PERIOD_1DAY = 86400
PERIOD_1SEC = 1
