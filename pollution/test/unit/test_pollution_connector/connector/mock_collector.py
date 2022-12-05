from __future__ import absolute_import, annotations

from pollution_connector.connector.collector import ConnectorCollector
from pollution_connector.connector.pollution import PollutionODHConnector
from pollution_connector.connector.traffic import TrafficODHConnector


class MockConnectorCollector(ConnectorCollector):

    @staticmethod
    def build() -> MockConnectorCollector:
        return MockConnectorCollector(
            traffic=TrafficODHConnector(
                base_reader_url="",
                base_writer_url="",
                authentication_url="",
                username="",
                password="",
                client_id="",
                client_secret="",
                grant_type=[""],
                pagination_size=1,
                max_post_batch_size=1,
                requests_timeout=1,
                requests_max_retries=1,
                requests_sleep_time=1,
                requests_retry_sleep_time=1
            ),
            pollution=PollutionODHConnector(
                base_reader_url="",
                base_writer_url="",
                authentication_url="",
                username="",
                password="",
                client_id="",
                client_secret="",
                grant_type=[""],
                pagination_size=1,
                max_post_batch_size=1,
                requests_timeout=1,
                requests_max_retries=1,
                requests_sleep_time=1,
                requests_retry_sleep_time=1
            )
        )
