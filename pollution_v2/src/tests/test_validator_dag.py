# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import importlib
from unittest import mock

import dateutil
from airflow.models import Variable

from common.settings import DEFAULT_TIMEZONE
from tests.test_common import TestDAGCommon


class TestValidatorDAG(TestDAGCommon):

    def test_pollution_computer_dag_import(self):
        """
        Test that the DAG is correctly imported.
        """
        assert self.dagbag.import_errors == {}
        assert self.dagbag.dags is not None
        assert self.validator_dag_id in self.dagbag.dags

        dag = self.dagbag.get_dag(dag_id=self.validator_dag_id)
        assert self.dagbag.import_errors == {}
        assert dag is not None

        dag_tasks = [self.get_stations_list_task_id, self.process_stations_task_id_validation, self.whats_next_task_id]
        assert len(dag.tasks) == len(dag_tasks)
        for task in dag_tasks:
            assert dag.has_task(task)

    def test_dag_task_dependencies(self):
        """
        Test that the tasks in the DAG are correctly connected.
        The task_dependencies dictionary contains the list of downstream tasks for each task.
        """
        dag = self.dagbag.get_dag(dag_id=self.validator_dag_id)
        for task_id, downstream_list in self.task_dependencies_validation.items():
            assert dag.has_task(task_id)
            task = dag.get_task(task_id)
            assert task.downstream_task_ids == set(downstream_list)
            if len(downstream_list) > 0:
                downstream_task = dag.get_task(downstream_list[0])
                assert task in downstream_task.upstream_list

    def test_pollution_computer_dag_starting_date(self):
        """
        Test that the DAG has the correct starting date from the ODH_MINIMUM_STARTING_DATE variable.
        Change the ODH_MINIMUM_STARTING_DATE variable in the environment and check the DAG starting date is updated.
        """
        starting_date = "2021-02-03"
        with ((mock.patch.dict("os.environ", AIRFLOW_VAR_ODH_MINIMUM_STARTING_DATE=starting_date))):
            # Reloading settings in order to update the ODH_MINIMUM_STARTING_DATE variable
            from common import settings
            importlib.reload(settings)
            assert starting_date == Variable.get("ODH_MINIMUM_STARTING_DATE")

            parsed_date = dateutil.parser.parse(starting_date)
            parsed_date = DEFAULT_TIMEZONE.localize(parsed_date)
            assert parsed_date == settings.ODH_MINIMUM_STARTING_DATE

            # Importing the dag after the settings have been reloaded
            from dags.aiaas_pollution_computer import dag as pollution_computer_dag
            assert parsed_date == pollution_computer_dag.start_date
            assert parsed_date == pollution_computer_dag.default_args["start_date"]
