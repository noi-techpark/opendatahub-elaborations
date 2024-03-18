# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from unittest.mock import patch, ANY, Mock

import pendulum

from common.data_model import TrafficSensorStation, StationLatestMeasure
from common.settings import DAG_POLLUTION_TRIGGER_DAG_HOURS_SPAN, ODH_MINIMUM_STARTING_DATE, DEFAULT_TIMEZONE
from tests.test_common import TestPollutionComputerCommon


class TestPollutionComputerDAGTasks(TestPollutionComputerCommon):

    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager.get_traffic_stations_from_cache")
    def test_get_traffic_station_is_called(self, get_traffic_stations_mock):
        """
        Test that the get_traffic_stations_from_cache method is called when the get_stations_list task is run.
        """
        # Run the get_stations_list task
        dag = self.dagbag.get_dag(dag_id=self.pollution_computer_dag_id)
        task = dag.get_task(self.get_stations_list_task_id)
        task_function = task.python_callable

        # Mock the stations_to_process parameter to be None
        task_function(**{
            "dag_run": Mock(conf={"stations_to_process": None})
        })

        get_traffic_stations_mock.assert_called_once()

    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager.get_traffic_stations_from_cache")
    def test_get_traffic_station_gets_stations_from_cache(self, get_traffic_stations_mock):
        """
        Test that the get_traffic_stations_from_cache method is called when the get_stations_list task is run.
        """
        # Run the get_stations_list task
        dag = self.dagbag.get_dag(dag_id=self.pollution_computer_dag_id)
        task = dag.get_task(self.get_stations_list_task_id)
        task_function = task.python_callable

        # Mock the available list of stations
        station_dict_2 = self.station_dict.copy()
        station_dict_2["code"] = "station_temp"
        get_traffic_stations_mock.return_value = [
            TrafficSensorStation.from_json(self.station_dict),
            TrafficSensorStation.from_json(station_dict_2)
        ]

        # Mock the stations_to_process parameter to be None
        return_value = task_function(**{
            "dag_run": Mock(conf={"stations_to_process": None})
        })

        # Test that the return value contains the entire list of stations
        self.assertEqual(return_value, [self.station_dict, station_dict_2])

    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager.get_traffic_stations_from_cache")
    def test_get_traffic_station_retrieves_passed_stations(self, get_traffic_stations_mock):
        """
        Test that the get_traffic_stations_from_cache method is called when the get_stations_list task is run.
        """
        # Run the get_stations_list task
        dag = self.dagbag.get_dag(dag_id=self.pollution_computer_dag_id)
        task = dag.get_task(self.get_stations_list_task_id)
        task_function = task.python_callable

        # Mock the available list of stations
        station_dict_2 = self.station_dict.copy()
        station_dict_2["code"] = "station_temp"
        get_traffic_stations_mock.return_value = [
            TrafficSensorStation.from_json(self.station_dict),
            TrafficSensorStation.from_json(station_dict_2)
        ]

        # Mock the stations_to_process parameter to be only one value
        return_value = task_function(**{
            "dag_run": Mock(conf={"stations_to_process": [self.station_dict["code"]]})
        })

        # Test that the return value contains only the passed station
        self.assertEqual(return_value, [self.station_dict])

    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager.run_computation_for_station")
    def test_run_computation_for_station_is_called(self, run_computation_for_station_mock):
        """
        Test that the run_computation_for_station method is called when the process_station task is run.
        """
        # Run the process_station task
        dag = self.dagbag.get_dag(dag_id=self.pollution_computer_dag_id)
        task = dag.get_task(self.process_station_task_id)
        task_function = task.python_callable
        task_function(self.station_dict)

        run_computation_for_station_mock.assert_called_once()

    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager.run_computation_for_station")
    def test_run_computation_for_station_gets_correct_input(self, run_computation_for_station_mock):
        """
        Test that the run_computation_for_station method is called when the process_station task is run.
        """
        # Run the process_station task
        dag = self.dagbag.get_dag(dag_id=self.pollution_computer_dag_id)
        task = dag.get_task(self.process_station_task_id)
        task_function = task.python_callable
        task_function(self.station_dict)

        run_computation_for_station_mock.assert_called_once_with(
            TrafficSensorStation.from_json(self.station_dict),
            ANY,  # This corresponds to the min_from_date parameter
            ANY   # This corresponds to the max_to_date parameter
        )

    # TODO restore
    @patch("airflow.operators.trigger_dagrun.TriggerDagRunOperator.execute")
    @patch("airflow.operators.trigger_dagrun.TriggerDagRunOperator.__init__")
    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager.get_all_latest_measures")
    def _test_trigger_next_dag_run_triggers_task_with_station(self, get_all_latest_measure_mock, trigger_dag_run_mock,
                                                             trigger_dag_run_execute_mock):
        """
        Test that the TriggerDagRunOperator is called when the whats_next task is run with a station with remaining data.
        """
        trigger_dag_run_mock.return_value = None

        # Mock self.station_dict to have remaining data
        included_date = pendulum.now().subtract(hours=DAG_POLLUTION_TRIGGER_DAG_HOURS_SPAN+1)
        get_all_latest_measure_mock.return_value = [
            StationLatestMeasure(self.station_dict["code"], included_date),
        ]

        # Run the whats_next task
        dag = self.dagbag.get_dag(dag_id=self.pollution_computer_dag_id)
        task = dag.get_task(self.whats_next_task_id)
        task_function = task.python_callable
        task_function([self.station_dict])

        # Test that the get_all_latest_measures method is called
        trigger_dag_run_mock.assert_called_once()

        # Test that the trigger_dag_run method is called
        trigger_dag_run_mock.assert_called_once_with(
            task_id="run_again_the_dag",
            dag=dag,
            trigger_dag_id=self.pollution_computer_dag_id,
            conf={"stations_to_process": [self.station_dict["code"]]}
        )
        trigger_dag_run_execute_mock.assert_called_once()

    # TODO restore
    @patch("airflow.operators.trigger_dagrun.TriggerDagRunOperator.execute")
    @patch("airflow.operators.trigger_dagrun.TriggerDagRunOperator.__init__")
    @patch("pollution_connector.manager.pollution_computation.PollutionComputationManager.get_all_latest_measures")
    def _test_trigger_next_dag_run_passes_correct_stations(self, get_all_latest_measures_mock, trigger_dag_run_mock,
                                                          trigger_dag_run_execute_mock):
        """
        Test that the trigger_next_dag_run method is called with the correct input when the whats_next task is run.
        """
        trigger_dag_run_mock.return_value = None

        span_hours = DAG_POLLUTION_TRIGGER_DAG_HOURS_SPAN
        included_date = pendulum.now().subtract(hours=span_hours+1)
        excluded_date = pendulum.now().subtract(hours=span_hours-1)
        get_all_latest_measures_mock.return_value = [
            StationLatestMeasure("station_1", included_date),
            StationLatestMeasure("station_2", excluded_date),
            StationLatestMeasure("station_3", included_date),
            StationLatestMeasure("station_4", excluded_date)
        ]

        # Run the whats_next task
        dag = self.dagbag.get_dag(dag_id=self.pollution_computer_dag_id)
        task = dag.get_task(self.whats_next_task_id)
        task_function = task.python_callable
        task_function([self.station_dict])

        # Test that the get_all_latest_measures method is called
        get_all_latest_measures_mock.assert_called_once()

        # Test that the trigger_dag_run method is called with the correct input
        trigger_dag_run_mock.assert_called_once_with(
            task_id="run_again_the_dag",
            dag=dag,
            trigger_dag_id=self.pollution_computer_dag_id,
            conf={"stations_to_process": ["station_1", "station_3"]}
        )

        trigger_dag_run_execute_mock.assert_called_once()

    def test_init_date_range(self):
        """
        Test that the init_date_range method returns the correct date range.
        """
        # Run the init_date_range method
        dag = self.dagbag.get_dag(dag_id=self.pollution_computer_dag_id)
        min_from_date, max_to_date = dag.init_date_range(None, None)

        # Test that the returned date range is correct
        self.assertEqual(min_from_date, DEFAULT_TIMEZONE.localize(ODH_MINIMUM_STARTING_DATE))
        assert max_to_date > min_from_date
