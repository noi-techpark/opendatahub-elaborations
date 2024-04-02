# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from datetime import datetime
from typing import Callable, Any
from unittest import TestCase
from unittest.mock import patch

from airflow.models import DagBag
import pendulum

from common.connector.common import ODHBaseConnector
from common.connector.validation import ValidationODHConnector
from common.data_model import TrafficSensorStation
from common.settings import DAG_POLLUTION_TRIGGER_DAG_HOURS_SPAN


class TestPollutionComputerCommon(TestCase):

    def setUp(self):
        self.dagbag = DagBag()
        self.pollution_computer_dag_id = "pollution_computer"

        # Task IDs
        self.get_stations_list_task_id = "get_stations_list"
        self.process_station_task_id = "process_station"
        self.whats_next_task_id = "whats_next"

        # For each task, the list of its downstream tasks
        self.task_dependencies = {
            self.get_stations_list_task_id: [self.process_station_task_id],
            self.process_station_task_id: [self.whats_next_task_id],
            self.whats_next_task_id: []
        }

        self.station_dict = {
            "code": "1",
            "active": "true",
            "available": "true",
            "coordinates": "1,1",
            "metadata": "metadata",
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

    def __mock_get_starting_date_allow_limited_stations(self, allowed_stations: list[dict]) -> Callable[[ODHBaseConnector, TrafficSensorStation, datetime], datetime]:
        span_hours = DAG_POLLUTION_TRIGGER_DAG_HOURS_SPAN
        ending_date = pendulum.now()
        included_starting_date = ending_date.subtract(hours=span_hours + 2)
        excluded_starting_date = ending_date.subtract(hours=span_hours - 2)
        def get_starting_date_mock(connector: ODHBaseConnector, traffic_station: TrafficSensorStation,
                                   min_from_date: datetime) -> datetime:
            if isinstance(connector, ValidationODHConnector):
                return ending_date
            else:
                if traffic_station.code in [station["code"] for station in allowed_stations]:
                    return included_starting_date
                return excluded_starting_date
        return get_starting_date_mock


    def mock_whats_next_run_allow_limited_stations(self, all_stations: list[dict], allowed_stations: list[dict]):
        with patch("dags.common.TrafficStationsDAG.get_stations_list") as get_stations_list_mock:
            with patch("common.manager.traffic_station.TrafficStationManager.get_starting_date") as get_starting_date_mock:

                # Mock allowed stations to have remaining data
                get_stations_list_mock.return_value = [
                    TrafficSensorStation.from_json(station_dict) for station_dict in all_stations
                ]
                get_starting_date_mock.side_effect = self.__mock_get_starting_date_allow_limited_stations(allowed_stations)

                # Run the whats_next task
                dag = self.dagbag.get_dag(dag_id=self.pollution_computer_dag_id)
                task = dag.get_task(self.whats_next_task_id)
                task_function = task.python_callable
                task_function(all_stations)
