# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from datetime import datetime
from typing import Callable, List
from unittest import TestCase
from unittest.mock import patch

from airflow.models import DagBag
import pendulum

from common.connector.common import ODHBaseConnector
from common.connector.traffic import TrafficODHConnector
from common.connector.validation import ValidationODHConnector
from common.data_model import TrafficSensorStation
from common.settings import DAG_POLLUTION_TRIGGER_DAG_HOURS_SPAN, DAG_VALIDATION_TRIGGER_DAG_HOURS_SPAN


class TestDAGCommon(TestCase):

    def setUp(self):
        self.dagbag = DagBag()
        self.pollution_computer_dag_id = "pollution_computer"
        self.validator_dag_id = "validator"

        # Task IDs
        self.get_stations_list_task_id = "get_stations_list"
        self.process_station_task_id_pollution = "process_station"
        self.process_stations_task_id_validation = "process_stations"
        self.whats_next_task_id = "whats_next"

        # For each task, the list of its downstream tasks
        self.task_dependencies_pollution = {
            self.get_stations_list_task_id: [self.process_station_task_id_pollution],
            self.process_station_task_id_pollution: [self.whats_next_task_id],
            self.whats_next_task_id: []
        }
        self.task_dependencies_validation = {
            self.get_stations_list_task_id: [self.process_stations_task_id_validation],
            self.process_stations_task_id_validation: [self.whats_next_task_id],
            self.whats_next_task_id: []
        }

        self.station_dict = {
            "code": "1",
            "active": "true",
            "available": "true",
            "coordinates": "1,1",
            "metadata": {"a22_metadata": "{\"metro\":\"123\"}"},
            "name": "station",
            "station_type": "type",
            "origin": "origin"
        }

        self.station2_dict = self.station_dict.copy()
        self.station2_dict["code"] = "2"

        self.station3_dict = self.station_dict.copy()
        self.station3_dict["code"] = "3"

        self.station4_dict = self.station_dict.copy()
        self.station4_dict["code"] = "4"

    def __mock_whats_next(self, all_stations: list[dict], allowed_stations: list[dict], dag_id: str,
                          get_starting_date_mock_func: Callable[[ODHBaseConnector, ODHBaseConnector,
                                                                 TrafficSensorStation, datetime, int], datetime]):

        with patch("dags.common.TrafficStationsDAG.get_stations_list") as get_stations_list_mock:
            with patch("common.manager.traffic_station.TrafficStationManager.get_starting_date") as get_starting_date_mock:

                # Mock allowed stations to have remaining data
                get_stations_list_mock.return_value = [
                    TrafficSensorStation.from_json(station_dict) for station_dict in all_stations
                ]
                get_starting_date_mock.side_effect = get_starting_date_mock_func

                # Run the whats_next task
                dag = self.dagbag.get_dag(dag_id=dag_id)
                task = dag.get_task(self.whats_next_task_id)
                task_function = task.python_callable
                task_function(all_stations)

    def mock_validator_whats_next_run_allow_limited_stations(self, all_stations: list[dict], allowed_stations: list[dict]):

        span_hours = DAG_VALIDATION_TRIGGER_DAG_HOURS_SPAN
        ending_date = pendulum.now()
        included_starting_date = ending_date.subtract(hours=span_hours + 2)
        excluded_starting_date = ending_date.subtract(hours=span_hours - 2)

        def get_starting_date_mock_func(output_connector: ODHBaseConnector, input_connector: ODHBaseConnector,
                                        stations: List[TrafficSensorStation], min_from_date: datetime,
                                        batch_size: int) -> datetime:
            if isinstance(output_connector, TrafficODHConnector):
                return ending_date
            else:
                allowed_station_codes = [station["code"] for station in allowed_stations]
                starting_dates = [included_starting_date
                                  if station.code in allowed_station_codes else excluded_starting_date
                                  for station in stations]
                return min(starting_dates)

        self.__mock_whats_next(all_stations, allowed_stations, self.validator_dag_id, get_starting_date_mock_func)

    def mock_pollution_computer_whats_next_run_allow_limited_stations(self, all_stations: list[dict], allowed_stations: list[dict]):

        span_hours = DAG_POLLUTION_TRIGGER_DAG_HOURS_SPAN
        ending_date = pendulum.now()
        included_starting_date = ending_date.subtract(hours=span_hours + 2)
        excluded_starting_date = ending_date.subtract(hours=span_hours - 2)

        def get_starting_date_mock_func(output_connector: ODHBaseConnector, input_connector: ODHBaseConnector,
                                        stations: List[TrafficSensorStation], min_from_date: datetime,
                                        batch_size: int) -> datetime:
            if isinstance(output_connector, ValidationODHConnector):
                return ending_date
            else:
                allowed_station_codes = [station["code"] for station in allowed_stations]
                starting_dates = [included_starting_date
                                  if station.code in allowed_station_codes else excluded_starting_date
                                  for station in stations]
                return min(starting_dates)

        self.__mock_whats_next(all_stations, allowed_stations, self.pollution_computer_dag_id, get_starting_date_mock_func)
