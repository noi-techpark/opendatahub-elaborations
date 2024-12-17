# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import requests
from datetime import timedelta, datetime

from airflow.decorators import task
from airflow.utils.trigger_rule import TriggerRule

from dags.common import StationsDAG
from common.connector.collector import ConnectorCollector
from common.data_model.common import Provenance
from common.data_model import Station, TrafficSensorStation
from common.settings import (ODH_MINIMUM_STARTING_DATE, PROVENANCE_ID, PROVENANCE_LINEAGE,
                             PROVENANCE_NAME_POLL_ELABORATION, PROVENANCE_VERSION, AIRFLOW_NUM_RETRIES,
                             DAG_POLLUTION_DISPERSAL_EXECUTION_CRONTAB, POLLUTION_DISPERSAL_STATION_MAPPING_ENDPOINT,
                             DAG_POLLUTION_DISPERSAL_TRIGGER_DAG_HOURS_SPAN,
                             ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL)
from pollution_dispersal.manager.pollution_dispersal import PollutionDispersalManager

# see https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html

logger = logging.getLogger("pollution_v2.dags.aiaas_pollution_dispersal")

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

THIS_DAG_ID = "pollution_dispersal"

with StationsDAG(
    THIS_DAG_ID,

    # execution interval if no backfill step length on date increment if backfill (interval determined by first slot
    # available in queue)
    # schedule_interval is deprecated
    schedule=DAG_POLLUTION_DISPERSAL_EXECUTION_CRONTAB,

    # execution date starting at (if needed, backfill)
    start_date=ODH_MINIMUM_STARTING_DATE,

    # if True, the scheduler creates a DAG Run for each completed interval between start_date and end_date
    # and the scheduler will execute them sequentially
    # no need to backfill with catch-up, we can rely on programmatically process-the-oldest-data-on-ODH
    catchup=False,

    tags=["aiaas", "pollution_dispersal"],

    # 1 as the maximum number of active DAG runs per DAG:
    # dag execution mode should be sequential to avoid periods overlapping and
    # to avoid quick and recent runs blocking slow and older ones (as ODH does not accept "older" data writing)
    max_active_runs=1,

    default_args=default_args
) as dag:

    def _init_manager() -> PollutionDispersalManager:
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
        manager = PollutionDispersalManager(connector_collector, provenance, checkpoint_cache)
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

        response = requests.get(POLLUTION_DISPERSAL_STATION_MAPPING_ENDPOINT)
        if (response.status_code != 200):
            logger.error(f"Failed to retrieve station mapping: {response.status_code} {response.text}")
            raise ValueError(f"Failed to retrieve station mapping: {response.status_code} {response.text}")
        logger.info(f"Retrieved station mapping: {response.text}")

        station_mapping = {}
        for x in response.json().values():
            if x["traffic_station_id"] in station_mapping:
                station_id = x["traffic_station_id"]
                previous = station_mapping[station_id]
                current = x["weather_station_id"]
                logger.warning(f"Duplicate station mapping entries for traffic_station_id [{station_id}]: "
                               f"First weather_station_id [{previous}], Second weather_station_id [{current}]")
            station_mapping[x["traffic_station_id"]] = x["weather_station_id"]

        # Serialization and deserialization is dependent on speed.
        # Use built-in functions like dict as much as you can and stay away
        # from using classes and other complex structures.
        station_dicts = []
        unique_station_codes = set()
        for station in stations_list:
            try:
                station_id = str(station.id_stazione)
            except ValueError:
                # some stations have different codes (such as "16:verso Bolzano"), so we skip them
                continue

            if station_id not in station_mapping:
                continue
            unique_station_codes.add(station_id)

            meteo_station_code = station_mapping[station_id]
            station.meteo_station_code = meteo_station_code

            station_dicts.append(station.to_json())

        logger.info(f"Retrieved {len(station_dicts)} stations")
        if len(unique_station_codes) == len(station_mapping):
            logger.info("All stations mapped in enabled domains have been retrieved: " + str(unique_station_codes))
        else:
            difference_str = str(unique_station_codes - set(station_mapping.keys()))
            logger.warning("Some stations mapped in enabled domains have not been retrieved: " + difference_str)

        return station_dicts


    @task
    def process_stations(station_dicts: list[dict], **kwargs):
        """
        Process a list of stations

        :param station_dicts: the stations to process
        """

        stations = [TrafficSensorStation.from_json(station_dict) for station_dict in station_dicts]
        logger.info(f"Received stations {stations}")

        manager = _init_manager()

        computation_start_dt = datetime.now()
        logger.info(f"Running computation")
        manager.run_computation_for_multiple_stations(stations)

        computation_end_dt = datetime.now()
        logger.info(f"Completed computation in [{(computation_end_dt - computation_start_dt).seconds}]")


    tmp = get_stations_list()

    processed_stations = process_stations(tmp)
