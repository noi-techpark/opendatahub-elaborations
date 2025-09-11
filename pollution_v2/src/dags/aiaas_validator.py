# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
from datetime import timedelta, datetime
from typing import List

from airflow.decorators import task
from airflow.utils.trigger_rule import TriggerRule
from redis.client import Redis

from common.cache.computation_checkpoint import ComputationCheckpointCache
from dags.common import TrafficStationsDAG
from common.connector.collector import ConnectorCollector
from common.data_model import TrafficSensorStation, Provenance
from common.settings import (ODH_MINIMUM_STARTING_DATE, DAG_VALIDATION_EXECUTION_CRONTAB, PROVENANCE_ID,
                             PROVENANCE_LINEAGE, PROVENANCE_NAME_VALIDATION, PROVENANCE_VERSION,
                             COMPUTATION_CHECKPOINT_REDIS_HOST, COMPUTATION_CHECKPOINT_REDIS_PORT,
                             COMPUTATION_CHECKPOINT_REDIS_DB, DEFAULT_TIMEZONE, DAG_VALIDATION_TRIGGER_DAG_HOURS_SPAN,
                             ODH_COMPUTATION_BATCH_SIZE_VALIDATION, AIRFLOW_NUM_RETRIES, get_now)
from validator.manager.validation import ValidationManager

# see https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html

logger = logging.getLogger("pollution_v2.dags.aiaas_validator")

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

THIS_DAG_ID = "validator"

with TrafficStationsDAG(
    THIS_DAG_ID,

    # execution interval if no backfill step length on date increment if backfill (interval determined by first slot
    # available in queue)
    # schedule_interval is deprecated
    schedule=DAG_VALIDATION_EXECUTION_CRONTAB,

    # execution date starting at (if needed, backfill)
    start_date=ODH_MINIMUM_STARTING_DATE,

    # if True, the scheduler creates a DAG Run for each completed interval between start_date and end_date
    # and the scheduler will execute them sequentially
    # no need to backfill with catch-up, we can rely on programmatically process-the-oldest-data-on-ODH
    catchup=False,

    tags=["aiaas", "validator"],

    # 1 as the maximum number of active DAG runs per DAG:
    # dag execution mode should be sequential to avoid periods overlapping and
    # to avoid quick and recent runs blocking slow and older ones (as ODH does not accept "older" data writing)
    max_active_runs=1,

    default_args=default_args
) as dag:
    def _init_manager() -> ValidationManager:
        """
        Inits what needed for the computation of a batch of pollution data measures.
        """

        checkpoint_cache = None
        if COMPUTATION_CHECKPOINT_REDIS_HOST:
            logger.info("Enabled checkpoint cache")
            checkpoint_cache = ComputationCheckpointCache(Redis(host=COMPUTATION_CHECKPOINT_REDIS_HOST,
                                                                port=COMPUTATION_CHECKPOINT_REDIS_PORT,
                                                                db=COMPUTATION_CHECKPOINT_REDIS_DB))
        else:
            logger.info("Checkpoint cache disabled")

        connector_collector = ConnectorCollector.build_from_env()
        provenance = Provenance(PROVENANCE_ID, PROVENANCE_LINEAGE, PROVENANCE_NAME_VALIDATION, PROVENANCE_VERSION)
        manager = ValidationManager(connector_collector, provenance, checkpoint_cache)
        return manager


    @task
    def get_stations_list(**kwargs) -> list[dict]:
        """
        Returns the complete list of stations or the filtered list based on previous DAG run

        :return: list of strings containing stations list
        """
        manager = _init_manager()

        stations_list = dag.get_stations_list(manager, True, True, True, **kwargs)

        # Serialization and deserialization is dependent on speed.
        # Use built-in functions like dict as much as you can and stay away
        # from using classes and other complex structures.
        station_dicts = [station.to_json() for station in stations_list]

        return station_dicts


    @task
    def process_stations(station_dicts: List[dict], **kwargs):
        """
        Retrieves and process all the stations

        :param station_dicts: list of stations dictionaries to be processed
        """

        stations_to_process = [TrafficSensorStation.from_json(station_dict) for station_dict in station_dicts]

        manager = _init_manager()

        min_from_date, max_to_date = dag.init_date_range(None, None)

        computation_start_dt = get_now()

        logger.info(f"Running validation from [{min_from_date.isoformat()}] to [{max_to_date.isoformat()}]")
        manager.run_computation(stations_to_process, min_from_date, max_to_date, ODH_COMPUTATION_BATCH_SIZE_VALIDATION,
                                True)

        computation_end_dt = get_now()
        logger.info(f"Completed validation in [{(computation_end_dt - computation_start_dt).seconds}]")


    @task(trigger_rule=TriggerRule.ALL_DONE)
    def whats_next(already_processed_stations, **kwargs):
        """
        Checks if there are still data to be processed before ending DAG runs

        :param already_processed_stations: the stations already processed (not used)
        """
        manager = _init_manager()

        def has_remaining_data(starting_date: datetime, ending_date: datetime) -> bool:
            """
            Determines if there are still enough data to be processed for another DAG run on the specific station.

            :param starting_date: the date on which data availability starts
            :param ending_date: the date on which data availability ends
            :return: true if there are enough data to run another DAG on this station
            """
            return (ending_date - starting_date).total_seconds() / 3600 > DAG_VALIDATION_TRIGGER_DAG_HOURS_SPAN

        dag.trigger_next_dag_run(manager, dag, has_remaining_data,
                                 ODH_COMPUTATION_BATCH_SIZE_VALIDATION,True, True, True, **kwargs)

    tmp = get_stations_list()

    processed_stations = process_stations(tmp)

    whats_next(processed_stations)
