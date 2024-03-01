# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from common.connector.pollution import PollutionODHConnector
from common.connector.traffic import TrafficODHConnector
from common.connector.validation import ValidationODHConnector
from common.settings import ODH_AUTHENTICATION_URL, ODH_USERNAME, ODH_PASSWORD, ODH_CLIENT_ID, \
    ODH_CLIENT_SECRET, ODH_PAGINATION_SIZE, REQUESTS_TIMEOUT, REQUESTS_MAX_RETRIES, REQUESTS_SLEEP_TIME, \
    REQUESTS_RETRY_SLEEP_TIME, ODH_BASE_READER_URL, ODH_BASE_WRITER_URL, ODH_GRANT_TYPE, ODH_MAX_POST_BATCH_SIZE


class ConnectorCollector:

    def __init__(self, traffic: TrafficODHConnector, validation: ValidationODHConnector, pollution: PollutionODHConnector):
        self.traffic = traffic
        self.validation = validation
        self.pollution = pollution

    @staticmethod
    def build_from_env() -> ConnectorCollector:
        base_reader_url = ODH_BASE_READER_URL
        base_writer_url = ODH_BASE_WRITER_URL
        authentication_url = ODH_AUTHENTICATION_URL
        user_name = ODH_USERNAME
        password = ODH_PASSWORD
        client_id = ODH_CLIENT_ID
        client_secret = ODH_CLIENT_SECRET
        grant_type = ODH_GRANT_TYPE
        pagination_size = ODH_PAGINATION_SIZE
        max_post_batch_size = ODH_MAX_POST_BATCH_SIZE
        requests_timeout = REQUESTS_TIMEOUT
        requests_max_retries = REQUESTS_MAX_RETRIES
        requests_sleep_time = REQUESTS_SLEEP_TIME
        requests_retry_sleep_time = REQUESTS_RETRY_SLEEP_TIME

        return ConnectorCollector(
            traffic=TrafficODHConnector(
                base_reader_url=base_reader_url,
                base_writer_url=base_writer_url,
                authentication_url=authentication_url,
                username=user_name,
                password=password,
                client_id=client_id,
                client_secret=client_secret,
                grant_type=grant_type,
                pagination_size=pagination_size,
                max_post_batch_size=max_post_batch_size,
                requests_timeout=requests_timeout,
                requests_max_retries=requests_max_retries,
                requests_sleep_time=requests_sleep_time,
                requests_retry_sleep_time=requests_retry_sleep_time
            ),
            validation=ValidationODHConnector(
                base_reader_url=base_reader_url,
                base_writer_url=base_writer_url,
                authentication_url=authentication_url,
                username=user_name,
                password=password,
                client_id=client_id,
                client_secret=client_secret,
                grant_type=grant_type,
                pagination_size=pagination_size,
                max_post_batch_size=max_post_batch_size,
                requests_timeout=requests_timeout,
                requests_max_retries=requests_max_retries,
                requests_sleep_time=requests_sleep_time,
                requests_retry_sleep_time=requests_retry_sleep_time
            ),
            pollution=PollutionODHConnector(
                base_reader_url=base_reader_url,
                base_writer_url=base_writer_url,
                authentication_url=authentication_url,
                username=user_name,
                password=password,
                client_id=client_id,
                client_secret=client_secret,
                grant_type=grant_type,
                pagination_size=pagination_size,
                max_post_batch_size=max_post_batch_size,
                requests_timeout=requests_timeout,
                requests_max_retries=requests_max_retries,
                requests_sleep_time=requests_sleep_time,
                requests_retry_sleep_time=requests_retry_sleep_time
            )
        )
