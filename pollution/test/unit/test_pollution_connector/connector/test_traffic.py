# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import datetime
from unittest import TestCase
from unittest.mock import patch, Mock, call

from requests import Response

from pollution_connector.connector.common import Token, ApiException, MaximumRetryExceeded
from pollution_connector.connector.traffic import TrafficODHConnector


class TestTrafficODHConnector(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.connector = TrafficODHConnector(
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
        self.connector._get_token = Mock(return_value=Token(access_token="",
                                                            expires_in=1,
                                                            refresh_expires_in=1,
                                                            refresh_token="",
                                                            token_type="",
                                                            not_before_policy="",
                                                            session_state="",
                                                            scope=[""],
                                                            created_at=datetime.datetime.now()))

    def test_get_request(self):
        with patch("requests.get") as request_get_mock:
            response = Response()
            response.status_code = 200
            response.json = Mock(return_value={})
            request_get_mock.return_value = response
            self.assertEqual({}, self.connector._get_request("path"))

    def test_get_request_api_exception(self):
        with patch("requests.get") as request_get_mock:
            response = Response()
            response.status_code = 400
            response._content = b""
            request_get_mock.return_value = response
            with self.assertRaises(ApiException):
                self.connector._get_request("path")

    def test_get_request_exception(self):
        with patch("requests.get") as request_get_mock:
            request_get_mock.side_effect = Exception()
            with self.assertRaises(MaximumRetryExceeded):
                self.connector._get_request("path")

            request_get_mock.assert_has_calls([call("path",
                                                    headers={
                                                        "Content-Type": "application/json",
                                                        "Authorization": "bearer "
                                                    },
                                                    params={},
                                                    timeout=1),
                                               call("path",
                                                    headers={
                                                        "Content-Type": "application/json",
                                                        "Authorization": "bearer "
                                                    },
                                                    params={},
                                                    timeout=1)])
