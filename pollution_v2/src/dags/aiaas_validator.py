# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
from datetime import timedelta, datetime

from airflow.decorators import task
from airflow.utils.trigger_rule import TriggerRule

from common.manager.traffic_station import TrafficStationManager
from dags.common import TrafficStationsDAG
from common.connector.collector import ConnectorCollector
from common.data_model import TrafficSensorStation, StationLatestMeasure
from common.settings import ODH_MINIMUM_STARTING_DATE, DAG_VALIDATION_EXECUTION_CRONTAB

# see https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html

logger = logging.getLogger("dags.aiaas_validator")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': ODH_MINIMUM_STARTING_DATE,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
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

    def _init_manager() -> TrafficStationManager:

        connector_collector = ConnectorCollector.build_from_env()
        manager = TrafficStationManager(connector_collector)
        return manager

    @task
    def get_stations_list(**kwargs) -> list[dict]:
        """
        Returns the complete list of stations or the filtered list based on previous DAG run

        :return: list of strings containing stations list
        """
        manager = _init_manager()

        station_dicts = dag.get_stations_list(manager, **kwargs)

        return station_dicts


    @task
    def process_station(station_dict: dict, **kwargs):
        """
        Process a single station

        :param station_dict: the station to process
        """

        station = TrafficSensorStation.from_json(station_dict)
        logger.info(f"Received station {station}")

        manager = _init_manager()

        min_from_date, max_to_date = dag.init_date_range(None, None)

        computation_start_dt = datetime.now()

        logger.info(f"running validation from {min_from_date} to {max_to_date}")

        # TODO: implement validation

        computation_end_dt = datetime.now()
        logger.info(f"Completed validation in [{(computation_end_dt - computation_start_dt).seconds}]")


    @task(trigger_rule=TriggerRule.ALL_DONE)
    def whats_next(already_processed_stations, **kwargs):
        """
        Checks if there are still data to be processed before ending DAG runs

        :param already_processed_stations: the stations already processed (not used)
        """
        manager = _init_manager()

        def has_remaining_data(measure: StationLatestMeasure) -> bool:
            # TODO: implement method to check if there are still data to be processed before ending DAG runs
            raise NotImplementedError

        dag.trigger_next_dag_run(manager, dag, has_remaining_data, **kwargs)


    processed_stations = process_station.expand(station_dict=get_stations_list())

    whats_next(processed_stations)
