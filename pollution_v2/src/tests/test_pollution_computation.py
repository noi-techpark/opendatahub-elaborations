# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import importlib
from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import patch, ANY

from airflow.models import Variable

from common.data_model import TrafficSensorStation
from common.settings import ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION, DEFAULT_TIMEZONE
from tests.test_common import TestDAGCommon


class TestPollutionComputation(TestDAGCommon):

    def setUp(self):

        super().setUp()

        self.min_date = DEFAULT_TIMEZONE.localize(datetime(2022, 1, 1))
        self.max_date = DEFAULT_TIMEZONE.localize(datetime(2024, 1, 31))
        self.latest_date = DEFAULT_TIMEZONE.localize(datetime(2024, 1, 30))

    @patch("dags.common.TrafficStationsDAG.init_date_range")
    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager._upload_data")
    @patch("pollution_connector.model.pollution_computation_model.PollutionComputationModel.compute_data")
    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager.get_starting_date")
    @patch("common.manager.traffic_station.TrafficStationManager._get_latest_date")
    @patch("common.manager.traffic_station.TrafficStationManager._download_traffic_data")
    def test_run_computation_date_range_daily(self, download_mock, latest_date_mock, get_start_date_mock,
                                              compute_mock, upload_mock, init_date_range_mock):
        """
        Test that the run_computation method is called with the correct date range.
        """
        batch_size = "30"
        with ((mock.patch.dict("os.environ", AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION=batch_size))):
            # Reloading settings in order to update the AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION variable
            from common import settings
            importlib.reload(settings)
            assert batch_size == Variable.get("ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION")

            # Get the process_station task
            dag = self.dagbag.get_dag(dag_id=self.pollution_computer_dag_id)
            task = dag.get_task(self.process_station_task_id_pollution)
            task_function = task.python_callable
            init_date_range_mock.return_value = (self.min_date, self.max_date)

            start_date = DEFAULT_TIMEZONE.localize(datetime(2024, 1, 30))
            get_start_date_mock.return_value = start_date

            # Start task to run computation
            task_function(self.station_dict)

            station = TrafficSensorStation.from_json(self.station_dict)

            get_start_date_mock.assert_called_once_with(ANY, ANY, [station], self.min_date, int(batch_size))
            latest_date_mock.assert_not_called()

            # Test that the run_computation method is called with the correct daily date range

            download_mock.assert_called_once_with(start_date, self.max_date, [station])
            compute_mock.assert_called_once()
            upload_mock.assert_called_once()

    @patch("dags.common.TrafficStationsDAG.init_date_range")
    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager._upload_data")
    @patch("pollution_connector.model.pollution_computation_model.PollutionComputationModel.compute_data")
    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager.get_starting_date")
    @patch("common.manager.traffic_station.TrafficStationManager._get_latest_date")
    @patch("common.manager.traffic_station.TrafficStationManager._download_traffic_data")
    def test_run_computation_date_range_when_more_data(self, download_mock, latest_date_mock, get_start_date_mock,
                                                       compute_mock, upload_mock, init_date_range_mock):
        """
        Test that the run_computation method is called with the correct date range.
        """
        batch_size = "30"
        with ((mock.patch.dict("os.environ", AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION=batch_size))):
            # Reloading settings in order to update the AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION variable
            from common import settings
            importlib.reload(settings)
            assert batch_size == Variable.get("ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION")

            # Get the process_station task
            dag = self.dagbag.get_dag(dag_id=self.pollution_computer_dag_id)
            task = dag.get_task(self.process_station_task_id_pollution)
            task_function = task.python_callable
            init_date_range_mock.return_value = (self.min_date, self.max_date)

            # start_date is the latest pollution found
            # latest_date is the latest traffic data found
            start_date = DEFAULT_TIMEZONE.localize(datetime(2023, 1, 1))
            latest_date_mock.return_value = self.latest_date
            get_start_date_mock.return_value = start_date

            # The correct end date is the start date plus the batch size
            correct_end_date = start_date + timedelta(days=ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION)

            # Start task to run computation
            task_function(self.station_dict)

            station = TrafficSensorStation.from_json(self.station_dict)

            get_start_date_mock.assert_called_once_with(ANY, ANY, [station], self.min_date, int(batch_size))
            if (self.max_date - start_date).days > ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION:
                latest_date_mock.assert_called_once_with(ANY, [station])
            else:
                latest_date_mock.assert_not_called()

            # Test that the run_computation method is called with the correct batch date range
            # A lot of data is available, so the end date is the start date plus the batch size
            download_mock.assert_called_once_with(start_date, correct_end_date, [station])
            compute_mock.assert_called_once()
            upload_mock.assert_called_once()

    @patch("dags.common.TrafficStationsDAG.init_date_range")
    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager._upload_data")
    @patch("pollution_connector.model.pollution_computation_model.PollutionComputationModel.compute_data")
    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager.get_starting_date")
    @patch("common.manager.traffic_station.TrafficStationManager._get_latest_date")
    @patch("common.manager.traffic_station.TrafficStationManager._download_traffic_data")
    def test_run_computation_date_range_when_few_data(self, download_mock, latest_date_mock, get_start_date_mock,
                                                      compute_mock, upload_mock, init_date_range_mock):
        """
        Test that the run_computation method is called with the correct date range.
        """
        batch_size = "30"
        with ((mock.patch.dict("os.environ", AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION=batch_size))):
            # Reloading settings in order to update the AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION variable
            from common import settings
            importlib.reload(settings)
            assert batch_size == Variable.get("ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION")

            # Get the process_station task
            dag = self.dagbag.get_dag(dag_id=self.pollution_computer_dag_id)
            task = dag.get_task(self.process_station_task_id_pollution)
            task_function = task.python_callable
            init_date_range_mock.return_value = (self.min_date, self.max_date)

            # start_date is the latest pollution found
            # latest_date is the latest traffic data found
            start_date = DEFAULT_TIMEZONE.localize(datetime(2024, 1, 15))
            latest_date_mock.return_value = self.latest_date
            get_start_date_mock.return_value = start_date

            # Start task to run computation
            task_function(self.station_dict)

            station = TrafficSensorStation.from_json(self.station_dict)
            get_start_date_mock.assert_called_once_with(ANY, ANY, [station], self.min_date, int(batch_size))
            if (self.max_date - start_date).days > ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION:
                latest_date_mock.assert_called_once_with(ANY, [station])
            else:
                latest_date_mock.assert_not_called()

            # Test that the run_computation method is called with the correct batch date range
            # Few data is available, so the end date is the max date
            download_mock.assert_called_once_with(start_date, self.max_date, [station])
            compute_mock.assert_called_once()
            upload_mock.assert_called_once()
