# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import argparse
import logging.config
from datetime import datetime
from typing import Optional

import dateutil.parser
import sentry_sdk
import yaml
from redis.client import Redis

from common.cache.computation_checkpoint import ComputationCheckpointCache
from common.connector.collector import ConnectorCollector
from common.data_model.common import Provenance
from common.logging import get_logging_configuration
from common.settings import (DEFAULT_TIMEZONE, SENTRY_SAMPLE_RATE, ODH_MINIMUM_STARTING_DATE,
                             COMPUTATION_CHECKPOINT_REDIS_HOST, COMPUTATION_CHECKPOINT_REDIS_PORT, PROVENANCE_ID,
                             PROVENANCE_LINEAGE, PROVENANCE_NAME_VALIDATION, PROVENANCE_VERSION,
                             COMPUTATION_CHECKPOINT_REDIS_DB, ODH_COMPUTATION_BATCH_SIZE_VALIDATION,
                             ROAD_WEATHER_CONFIG_FILE)
from road_weather.manager.road_weather import RoadWeatherManager
from validator.manager.validation import ValidationManager

logging.config.dictConfig(get_logging_configuration("pollution_v2"))

logger = logging.getLogger("pollution_v2.main_road_weather")

sentry_sdk.init(
    traces_sample_rate=SENTRY_SAMPLE_RATE,
    integrations=[]
)


# not used anymore after refactoring from Celery to Airflow
def compute_data() -> None:
    """
    Start the computation of a batch of traffic data measures to be validated. As starting date for the batch is used
    the latest validated measure available on the ODH, if no validated measures are available min_from_date is used.
    """

    collector_connector = ConnectorCollector.build_from_env()
    provenance = Provenance(PROVENANCE_ID, PROVENANCE_LINEAGE, PROVENANCE_NAME_VALIDATION, PROVENANCE_VERSION)
    manager = RoadWeatherManager(collector_connector, provenance)

    stations_list = manager.get_station_list()

    with open(ROAD_WEATHER_CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)
        whitelist = config.get('whitelist', [])
        station_mapping = {str(k): str(v) for k, v in config['mappings'].items()}

    if whitelist:
        whitelist = list(map(str, whitelist))
        logger.info(f"Filtering stations with whitelist: {whitelist}")
        stations_list = [station for station in stations_list if str(station.code) in whitelist]

    # Serialization and deserialization is dependent on speed.
    # Use built-in functions like dict as much as you can and stay away
    # from using classes and other complex structures.
    station_dicts = []
    for station in stations_list:
        if str(station.code) not in station_mapping:
            logger.error(f"Station code [{station.code}] not found in the mapping [{ROAD_WEATHER_CONFIG_FILE}]")
            raise ValueError(f"Station code [{station.code}] not found in the mapping")

        logger.info("Found mapping for ODH station code "
                    "[" + str(str(station.code)) + "] -> CISMA station code "
                                                   "[" + str(station_mapping[station.code]) + "]")
        logger.info(f"Downloading forecast data for station [{station.code}] from CISMA")
        wrf_station_code = station_mapping[str(station.code)]
        station.wrf_code = wrf_station_code

    for station in stations_list:
        manager.run_computation_for_single_station(station)


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description="Manually run a road weather forecast")

    arg_parser.add_argument("--run-async", action="store_true", help="If set it run the task in the celery cluster")

    compute_data()
    '''if args.run_async:
        task: AsyncResult = compute_data.delay(min_from_date=from_date, max_to_date=to_date)
        logger.info(f"Scheduled async pollution computation. Task ID: [{task.task_id}]")
    else:
        logger.info("Staring pollution computation")
        compute_data(min_from_date=from_date, max_to_date=to_date)'''
