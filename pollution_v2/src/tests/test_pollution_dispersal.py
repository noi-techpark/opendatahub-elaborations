# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import importlib
from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import patch, ANY, MagicMock

from airflow.models import Variable

from common.data_model import TrafficSensorStation, PollutionMeasureCollection, RoadWeatherObservationMeasureCollection
from common.data_model.weather import WeatherMeasureCollection
from common.settings import ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL, DEFAULT_TIMEZONE, \
    POLLUTION_DISPERSAL_COMPUTATION_HOURS_SPAN
from tests.test_common import TestDAGCommon


class TestPollutionDispersalComputation(TestDAGCommon):

    def setUp(self):

        super().setUp()

        self.min_date = DEFAULT_TIMEZONE.localize(datetime(2022, 1, 1))
        self.max_date = DEFAULT_TIMEZONE.localize(datetime(2024, 1, 30, 1))
        self.latest_date = DEFAULT_TIMEZONE.localize(datetime(2024, 1, 30))

        self.init_date_range_mock = None
        self.upload_mock = None
        self.compute_mock = None
        self.get_start_date_mock = None
        self.latest_date_mock = None
        self.pollution_mock = None
        self.weather_mock = None
        self.road_weather_mock = None
        self.domain_mock = None
        self.post_stations_mock = None
        self.entries_mock = None
        self.log_mock = None
        self.rmtree_mock = None
        self.os_remove_mock = None


    @staticmethod
    def _apply_pollution_dispersal_mocks(func: callable):
        def wrap(*args, **kwargs):
            test_self = args[0]
            with patch("dags.common.TrafficStationsDAG.init_date_range") as init_date_range_mock, \
                 patch("pollution_dispersal.manager.pollution_dispersal.PollutionDispersalManager._upload_data") as upload_mock, \
                 patch("pollution_dispersal.model.pollution_dispersal_model.PollutionDispersalModel.compute_data") as compute_mock, \
                 patch("pollution_dispersal.manager.pollution_dispersal.PollutionDispersalManager.get_starting_date") as get_start_date_mock, \
                 patch("common.manager.traffic_station.TrafficStationManager._get_latest_date") as latest_date_mock, \
                 patch("pollution_dispersal.manager.pollution_dispersal.PollutionDispersalManager._download_pollution_data") as pollution_mock, \
                 patch("pollution_dispersal.manager.pollution_dispersal.PollutionDispersalManager._download_weather_data") as weather_mock, \
                 patch("pollution_dispersal.manager.pollution_dispersal.PollutionDispersalManager._download_road_weather_data") as road_weather_mock, \
                 patch("pollution_dispersal.manager.pollution_dispersal.PollutionDispersalManager._get_domain_mapping") as domain_mock, \
                 patch("common.connector.pollution_dispersal.PollutionDispersalODHConnector.post_stations") as post_stations_mock, \
                 patch("pollution_dispersal.model.pollution_dispersal_model.PollutionDispersalModel.get_pollution_dispersal_entries_from_folder") as entries_mock, \
                 patch("pollution_dispersal.manager.pollution_dispersal.PollutionDispersalManager._log_skipped_domains") as log_mock, \
                 patch("shutil.rmtree") as rmtree_mock, \
                 patch("os.remove") as os_remove_mock:

                test_self.init_date_range_mock = init_date_range_mock
                test_self.upload_mock = upload_mock
                test_self.compute_mock = compute_mock
                test_self.get_start_date_mock = get_start_date_mock
                test_self.latest_date_mock = latest_date_mock
                test_self.pollution_mock = pollution_mock
                test_self.weather_mock = weather_mock
                test_self.road_weather_mock = road_weather_mock
                test_self.domain_mock = domain_mock
                test_self.post_stations_mock = post_stations_mock
                test_self.entries_mock = entries_mock
                test_self.log_mock = log_mock
                test_self.rmtree_mock = rmtree_mock
                test_self.os_remove_mock = os_remove_mock

                test_self.domain_mock.return_value = TestPollutionDispersalComputation._mock_domain_mapping()
                test_self.entries_mock.return_value = [MagicMock], [MagicMock]
                test_self.compute_mock.return_value = "fake_folder_name"
                test_self.pollution_mock.return_value = [PollutionMeasureCollection([MagicMock])]  # noqa
                test_self.weather_mock.return_value = [WeatherMeasureCollection([MagicMock])]  # noqa
                test_self.road_weather_mock.return_value = [RoadWeatherObservationMeasureCollection([MagicMock])]  # noqa

                return func(*args, **kwargs)
        return wrap

    @staticmethod
    def _mock_domain_mapping() -> dict:
        return {
            "1": {
                "traffic_station_id": "1",
                "weather_station_id": "w1",
                "description": "description1",
            },
            "2": {
                "traffic_station_id": "2",
                "weather_station_id": "w2",
                "description": "description2",
            }
        }

    @_apply_pollution_dispersal_mocks
    def test_run_computation_date_range_daily(self):
        """
        Test that the run_computation method is called with the correct date range.
        """
        batch_size = "30"
        with ((mock.patch.dict("os.environ", AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL=batch_size))):
            # Reloading settings in order to update the AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL variable
            from common import settings
            importlib.reload(settings)
            assert batch_size == Variable.get("ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL")

            # Get the process_station task
            dag = self.dagbag.get_dag(dag_id=self.pollution_dispersal_dag_id)
            task = dag.get_task(self.process_stations_task_id_dispersal)
            task_function = task.python_callable
            self.init_date_range_mock.return_value = (self.min_date, self.max_date)

            start_date = DEFAULT_TIMEZONE.localize(datetime(2024, 1, 30))
            self.get_start_date_mock.return_value = start_date

            # Start task to run computation
            task_function([self.station_dict])

            station = TrafficSensorStation.from_json(self.station_dict)

            self.get_start_date_mock.assert_called_once_with(ANY, ANY, [station], self.min_date, int(batch_size), True)
            self.latest_date_mock.assert_not_called()

            # Test that the run_computation method is called with the correct daily date range

            self.pollution_mock.assert_called_once_with(start_date, self.max_date, [station])
            self.weather_mock.assert_called_once_with(start_date, self.max_date, [station])
            self.road_weather_mock.assert_called_once_with(start_date, self.max_date, [station])
            self.compute_mock.assert_called_once()
            self.upload_mock.assert_called_once()
            self.post_stations_mock.assert_called_once()

    @_apply_pollution_dispersal_mocks
    def test_run_computation_date_range_when_more_data(self):
        """
        Test that the run_computation method is called with the correct date range.
        """
        batch_size = "30"
        with ((mock.patch.dict("os.environ", AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL=batch_size))):
            # Reloading settings in order to update the AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL variable
            from common import settings
            importlib.reload(settings)
            assert batch_size == Variable.get("ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL")

            # Get the process_station task
            dag = self.dagbag.get_dag(dag_id=self.pollution_dispersal_dag_id)
            task = dag.get_task(self.process_stations_task_id_dispersal)
            task_function = task.python_callable
            self.init_date_range_mock.return_value = (self.min_date, self.max_date)

            # start_date is the latest pollution found
            # latest_date is the latest traffic data found
            start_date = DEFAULT_TIMEZONE.localize(datetime(2023, 1, 1))
            self.latest_date_mock.return_value = self.latest_date
            self.get_start_date_mock.return_value = start_date

            # The correct end date is the start date plus the batch size
            correct_end_date = start_date + timedelta(hours=POLLUTION_DISPERSAL_COMPUTATION_HOURS_SPAN)
            # Start task to run computation
            task_function([self.station_dict])

            station = TrafficSensorStation.from_json(self.station_dict)

            self.get_start_date_mock.assert_called_once_with(ANY, ANY, [station], self.min_date, int(batch_size), True)
            if (self.max_date - start_date).days > ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL:
                self.latest_date_mock.assert_called_once_with(ANY, [station])
            else:
                self.latest_date_mock.assert_not_called()

            # Test that the run_computation method is called with the correct batch date range
            # A lot of data is available, so the end date is the start date plus the batch size
            self.pollution_mock.assert_called_once_with(start_date, correct_end_date, [station])
            self.weather_mock.assert_called_once_with(start_date, correct_end_date, [station])
            self.road_weather_mock.assert_called_once_with(start_date, correct_end_date, [station])
            self.compute_mock.assert_called_once()
            self.upload_mock.assert_called_once()
            self.post_stations_mock.assert_called_once()

    @_apply_pollution_dispersal_mocks
    def test_run_computation_date_range_when_few_data(self):
        """
        Test that the run_computation method is called with the correct date range.
        """
        batch_size = "30"
        with ((mock.patch.dict("os.environ", AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL=batch_size))):
            # Reloading settings in order to update the AIRFLOW_VAR_ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL variable
            from common import settings
            importlib.reload(settings)
            assert batch_size == Variable.get("ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL")

            # Get the process_station task
            dag = self.dagbag.get_dag(dag_id=self.pollution_dispersal_dag_id)
            task = dag.get_task(self.process_stations_task_id_dispersal)
            task_function = task.python_callable
            self.init_date_range_mock.return_value = (self.min_date, self.max_date)

            # start_date is the latest pollution found
            # latest_date is the latest traffic data found
            start_date = DEFAULT_TIMEZONE.localize(datetime(2024, 1, 30, 0, 30))
            self.latest_date_mock.return_value = self.latest_date
            self.get_start_date_mock.return_value = start_date

            # Start task to run computation
            task_function([self.station_dict])

            station = TrafficSensorStation.from_json(self.station_dict)
            self.get_start_date_mock.assert_called_once_with(ANY, ANY, [station], self.min_date, int(batch_size), True)
            if (self.max_date - start_date).days > ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL:
                self.latest_date_mock.assert_called_once_with(ANY, [station])
            else:
                self.latest_date_mock.assert_not_called()

            # Test that the run_computation method is called with the correct batch date range
            # Few data is available, so the end date is the max date
            self.pollution_mock.assert_called_once_with(start_date, self.max_date, [station])
            self.weather_mock.assert_called_once_with(start_date, self.max_date, [station])
            self.road_weather_mock.assert_called_once_with(start_date, self.max_date, [station])
            self.compute_mock.assert_called_once()
            self.upload_mock.assert_called_once()
            self.post_stations_mock.assert_called_once()
