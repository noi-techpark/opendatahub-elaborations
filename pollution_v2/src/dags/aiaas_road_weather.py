# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
from datetime import timedelta, datetime

import yaml
from airflow.decorators import task
from redis.client import Redis

from dags.common import StationsDAG
from common.cache.computation_checkpoint import ComputationCheckpointCache
from common.connector.collector import ConnectorCollector
from common.data_model.common import Provenance
from common.data_model import Station
from common.settings import (ODH_MINIMUM_STARTING_DATE, COMPUTATION_CHECKPOINT_REDIS_DB,
                             COMPUTATION_CHECKPOINT_REDIS_PORT, COMPUTATION_CHECKPOINT_REDIS_HOST,
                             PROVENANCE_ID, PROVENANCE_LINEAGE, PROVENANCE_NAME_POLL_ELABORATION,
                             PROVENANCE_VERSION, DEFAULT_TIMEZONE, ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION,
                             AIRFLOW_NUM_RETRIES, DAG_ROAD_WEATHER_EXECUTION_CRONTAB, ROAD_WEATHER_CONFIG_FILE)
from road_weather.manager.road_weather import RoadWeatherManager

# see https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html

logger = logging.getLogger("pollution_v2.dags.aiaas_road_weather")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': ODH_MINIMUM_STARTING_DATE,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': AIRFLOW_NUM_RETRIES,
    'retry_delay': timedelta(minutes=5),
}

THIS_DAG_ID = "road_weather"

with StationsDAG(
    THIS_DAG_ID,

    # execution interval if no backfill step length on date increment if backfill (interval determined by first slot
    # available in queue)
    # schedule_interval is deprecated
    schedule=DAG_ROAD_WEATHER_EXECUTION_CRONTAB,

    # execution date starting at (if needed, backfill)
    start_date=ODH_MINIMUM_STARTING_DATE,

    # if True, the scheduler creates a DAG Run for each completed interval between start_date and end_date
    # and the scheduler will execute them sequentially
    # no need to backfill with catch-up, we can rely on programmatically process-the-oldest-data-on-ODH
    catchup=False,

    tags=["aiaas", "road_weather"],

    # 1 as the maximum number of active DAG runs per DAG:
    # dag execution mode should be sequential to avoid periods overlapping and
    # to avoid quick and recent runs blocking slow and older ones (as ODH does not accept "older" data writing)
    max_active_runs=1,

    default_args=default_args
) as dag:

    def _init_manager() -> RoadWeatherManager:
        """
        Inits what needed for the computation of a batch of pollution data measures.
        """

        checkpoint_cache = None
        # TODO: decide if we want to use the checkpoint cache
        # if COMPUTATION_CHECKPOINT_REDIS_HOST:
        #     logger.info("Enabled checkpoint cache")
        #     checkpoint_cache = ComputationCheckpointCache(Redis(host=COMPUTATION_CHECKPOINT_REDIS_HOST,
        #                                                         port=COMPUTATION_CHECKPOINT_REDIS_PORT,
        #                                                         db=COMPUTATION_CHECKPOINT_REDIS_DB))
        # else:
        #     logger.info("Checkpoint cache disabled")

        connector_collector = ConnectorCollector.build_from_env()
        provenance = Provenance(PROVENANCE_ID, PROVENANCE_LINEAGE, PROVENANCE_NAME_POLL_ELABORATION, PROVENANCE_VERSION)
        manager = RoadWeatherManager(connector_collector, provenance, checkpoint_cache)
        return manager

    @task
    def get_stations_list(**kwargs) -> list[dict]:
        """
        Returns the complete list of stations or the filtered list based on previous DAG run

        :return: list of strings containing stations list
        """
        logger.info("Retrieving stations list")
        manager = _init_manager()

        stations_list = dag.get_stations_list(manager, **kwargs)
        logger.info("Found station codes: " + str([station.code for station in stations_list]))

        with open(ROAD_WEATHER_CONFIG_FILE, 'r') as file:
            config = yaml.safe_load(file)
            whitelist = config.get('whitelist', [])

        if whitelist:
            whitelist = list(map(str, whitelist))
            logger.info(f"Filtering stations with whitelist: {whitelist}")
            stations_list = [station for station in stations_list if str(station.code) in whitelist]

        # Serialization and deserialization is dependent on speed.
        # Use built-in functions like dict as much as you can and stay away
        # from using classes and other complex structures.
        station_dicts = [station.to_json() for station in stations_list]
        logger.info(f"Retrieved {len(station_dicts)} stations")

        # TODO restore full list
        return station_dicts[:2]


    @task
    def process_station(station_dict: dict, **kwargs):
        """
        Process a single station

        :param station_dict: the station to process
        """

        station = Station.from_json(station_dict)
        logger.info(f"Received station {station}")

        manager = _init_manager()

        # TODO: are the dates needed? backfill?
        # min_from_date, max_to_date = dag.init_date_range(None, None)

        computation_start_dt = datetime.now()
        # logger.info(f"Running computation from [{min_from_date}] to [{max_to_date}]")
        logger.info(f"Running computation")
        manager.run_computation_for_single_station(station)

        # TODO: run container with METRo

        computation_end_dt = datetime.now()
        logger.info(f"Completed computation in [{(computation_end_dt - computation_start_dt).seconds}]")


    processed_stations = process_station.expand(station_dict=get_stations_list())
