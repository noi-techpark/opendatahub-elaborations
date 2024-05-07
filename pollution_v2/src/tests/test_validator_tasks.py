# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from unittest.mock import patch, ANY, Mock

from common.data_model import TrafficSensorStation
from common.settings import ODH_MINIMUM_STARTING_DATE, DEFAULT_TIMEZONE
from tests.test_common import TestDAGCommon


class TestValidatorDAGTasks(TestDAGCommon):

    @patch("validator.manager.validation.ValidationManager.get_traffic_stations_from_cache")
    def test_get_traffic_station_is_called(self, get_traffic_stations_mock):
        """
        Test that the get_traffic_stations_from_cache method is called when the get_stations_list task is run.
        """
        # Run the get_stations_list task
        dag = self.dagbag.get_dag(dag_id=self.validator_dag_id)
        task = dag.get_task(self.get_stations_list_task_id)
        task_function = task.python_callable

        # Mock the stations_to_process parameter to be None
        task_function(**{
            "dag_run": Mock(conf={"stations_to_process": None})
        })

        get_traffic_stations_mock.assert_called_once()

    @patch("validator.manager.validation.ValidationManager.get_traffic_stations_from_cache")
    def test_get_traffic_station_gets_stations_from_cache(self, get_traffic_stations_mock):
        """
        Test that the get_traffic_stations_from_cache method is called when the get_stations_list task is run.
        """
        # Run the get_stations_list task
        dag = self.dagbag.get_dag(dag_id=self.validator_dag_id)
        task = dag.get_task(self.get_stations_list_task_id)
        task_function = task.python_callable

        # Mock the available list of stations
        get_traffic_stations_mock.return_value = [
            TrafficSensorStation.from_json(self.station_dict),
            TrafficSensorStation.from_json(self.station2_dict)
        ]

        # Mock the stations_to_process parameter to be None
        return_value = task_function(**{
            "dag_run": Mock(conf={"stations_to_process": None})
        })

        # Test that the return value contains the entire list of stations
        self.assertEqual(return_value, [self.station_dict, self.station2_dict])

    @patch("validator.manager.validation.ValidationManager.get_traffic_stations_from_cache")
    def test_get_traffic_station_retrieves_passed_stations(self, get_traffic_stations_mock):
        """
        Test that the get_traffic_stations_from_cache method is called when the get_stations_list task is run.
        """
        # Run the get_stations_list task
        dag = self.dagbag.get_dag(dag_id=self.validator_dag_id)
        task = dag.get_task(self.get_stations_list_task_id)
        task_function = task.python_callable

        # Mock the available list of stations
        get_traffic_stations_mock.return_value = [
            TrafficSensorStation.from_json(self.station_dict),
            TrafficSensorStation.from_json(self.station2_dict)
        ]

        # Mock the stations_to_process parameter to be only one value
        return_value = task_function(**{
            "dag_run": Mock(conf={"stations_to_process": [self.station_dict["code"]]})
        })

        # Test that the return value contains only the passed station
        self.assertEqual(return_value, [self.station_dict])

    @patch("validator.manager.validation.ValidationManager.run_computation")
    def test_run_computation_is_called(self, run_computation_mock):
        """
        Test that the run_computation method is called when the process_station task is run.
        """
        # Run the process_station task
        dag = self.dagbag.get_dag(dag_id=self.validator_dag_id)
        task = dag.get_task(self.process_station_task_id)
        task_function = task.python_callable
        task_function(self.station_dict)

        run_computation_mock.assert_called_once()

    @patch("validator.manager.validation.ValidationManager.run_computation")
    def test_run_computation_gets_correct_input(self, run_computation_mock):
        """
        Test that the run_computation method is called when the process_station task is run.
        """
        # Run the process_station task
        dag = self.dagbag.get_dag(dag_id=self.validator_dag_id)
        task = dag.get_task(self.process_station_task_id)
        task_function = task.python_callable
        task_function(self.station_dict)

        run_computation_mock.assert_called_once_with(
            TrafficSensorStation.from_json(self.station_dict),
            ANY,  # This corresponds to the min_from_date parameter
            ANY   # This corresponds to the max_to_date parameter
        )

    @patch("airflow.operators.trigger_dagrun.TriggerDagRunOperator.execute")
    @patch("airflow.operators.trigger_dagrun.TriggerDagRunOperator.__init__")
    def test_trigger_next_dag_run_triggers_task_with_station(self, trigger_dag_run_mock, trigger_dag_run_execute_mock):
        """
        Test that the TriggerDagRunOperator is called when the whats_next task is run with a station with remaining data.
        """
        trigger_dag_run_mock.return_value = None

        all_stations = [self.station_dict, self.station2_dict]
        self.mock_validator_whats_next_run_allow_limited_stations(all_stations, all_stations)

        # Test that the trigger_dag_run method is called
        dag = self.dagbag.get_dag(dag_id=self.validator_dag_id)
        trigger_dag_run_mock.assert_called_once_with(
            task_id="run_again_the_dag",
            dag=dag,
            trigger_dag_id=self.validator_dag_id,
            conf={"stations_to_process": [station['code'] for station in all_stations]}
        )
        trigger_dag_run_execute_mock.assert_called_once()

    @patch("airflow.operators.trigger_dagrun.TriggerDagRunOperator.execute")
    @patch("airflow.operators.trigger_dagrun.TriggerDagRunOperator.__init__")
    def test_trigger_next_dag_run_passes_correct_stations(self, trigger_dag_run_mock, trigger_dag_run_execute_mock):
        """
        Test that the trigger_next_dag_run method is called with the correct input when the whats_next task is run.
        """
        trigger_dag_run_mock.return_value = None

        all_stations = [self.station_dict, self.station2_dict, self.station3_dict, self.station4_dict]
        allowed_stations = [self.station_dict, self.station3_dict]
        self.mock_validator_whats_next_run_allow_limited_stations(all_stations, allowed_stations)

        # Test that the trigger_dag_run method is called with the correct input
        dag = self.dagbag.get_dag(dag_id=self.validator_dag_id)
        trigger_dag_run_mock.assert_called_once_with(
            task_id="run_again_the_dag",
            dag=dag,
            trigger_dag_id=self.validator_dag_id,
            conf={"stations_to_process": [station['code'] for station in allowed_stations]}
        )

        trigger_dag_run_execute_mock.assert_called_once()

    def test_init_date_range(self):
        """
        Test that the init_date_range method returns the correct date range.
        """
        # Run the init_date_range method
        dag = self.dagbag.get_dag(dag_id=self.validator_dag_id)
        min_from_date, max_to_date = dag.init_date_range(None, None)

        # Test that the returned date range is correct
        self.assertEqual(min_from_date, DEFAULT_TIMEZONE.localize(ODH_MINIMUM_STARTING_DATE))
        assert max_to_date > min_from_date
