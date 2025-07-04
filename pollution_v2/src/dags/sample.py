# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import textwrap
from datetime import datetime, timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from keycloak import KeycloakOpenID

from common.settings import ODH_AUTHENTICATION_URL, ODH_CLIENT_ID, ODH_CLIENT_SECRET, \
    ODH_USERNAME, ODH_PASSWORD, ODH_GRANT_TYPE

print(os.environ)

# https://airflow.apache.org/docs/apache-airflow/2.8.1/core-concepts/dag-run.html

with DAG(
    "sample",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "email": ["marco.angheben@u-hopper.com"],
        "email_on_failure": True,
        "email_on_retry": True,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'trigger_rule': 'all_success'
    },
    description="A simple sample DAG",

    # execution interval if no backfill
    # step length on date increment if backfill (interval determined by first slot available in queue)
    schedule=timedelta(minutes=5),

    # execution date starting at (if needed, backfill)
    start_date=datetime(2024, 1, 1),

    # if True, the scheduler creates a DAG Run for each completed interval between start_date and end_date
    # and the scheduler will execute them sequentially
    catchup=True,

    tags=["example"],
) as dag:
    def print_context(ds, **kwargs):
        """Print the Airflow context and ds variable from the context."""

        print("reading kwargs")
        for key, value in kwargs.items():
            print(f"> {key} - {value}")

        print("reading Python path")
        import sys
        from pprint import pprint
        pprint(sys.path)

        print(f"connecting to {ODH_AUTHENTICATION_URL} with {ODH_CLIENT_ID} and its secret key")
        _keycloak_openid = KeycloakOpenID(server_url=ODH_AUTHENTICATION_URL, client_id=ODH_CLIENT_ID,
                                          realm_name="noi", client_secret_key=ODH_CLIENT_SECRET)
        print(f"  calling...")
        tmp = _keycloak_openid.token(username=ODH_USERNAME, password=ODH_PASSWORD, grant_type=ODH_GRANT_TYPE)
        print(f"  we got token! {tmp}")

        start_date = kwargs["data_interval_start"]
        end_date = kwargs["data_interval_end"]
        print(f"Data interval start: {start_date.isoformat()} and end: {end_date.isoformat()}")

        return 'Whatever you return gets printed in the logs'


    # https://airflow.apache.org/docs/apache-airflow/2.2.0/howto/operator/python.html
    t0 = PythonOperator(
        task_id='print_the_context',
        python_callable=print_context,
    )

    # t1, t2 and t3 are examples of tasks created by instantiating operators
    t1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    t2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        bash_command="sleep 5",
        retries=3,
    )
    t1.doc_md = textwrap.dedent(
        """\
    #### Task Documentation
    You can document your task using the attributes `doc_md` (markdown),
    `doc` (plain text), `doc_rst`, `doc_json`, `doc_yaml` which gets
    rendered in the UI's Task Instance Details page.
    ![img](http://montcs.bloomu.edu/~bobmon/Semesters/2012-01/491/import%20soul.png)
    **Image Credit:** Randall Munroe, [XKCD](https://xkcd.com/license.html)
    """
    )

    dag.doc_md = __doc__  # providing that you have a docstring at the beginning of the DAG; OR
    dag.doc_md = """
    This is a documentation placed anywhere
    """  # otherwise, type it like this
    templated_command = textwrap.dedent(
        """
    {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(ds, 7)}}"
    {% endfor %}
    """
    )

    t3 = BashOperator(
        task_id="templated",
        depends_on_past=False,
        bash_command=templated_command,
    )

    t0 >> [t1, t2] >> t3
