# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from unittest import TestCase

from airflow.models import DagBag


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
