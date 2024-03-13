# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: CC0-1.0

FROM apache/airflow:2.8.1-python3.11
USER root
RUN apt update
RUN apt install -y gcc g++ build-essential
USER airflow
COPY requirements.txt .
RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt
# providers for writing logs on S3
RUN pip install apache-airflow-providers-amazon
ADD src/ /opt/airflow/dags