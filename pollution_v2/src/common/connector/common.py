# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Generic, List

import requests
from keycloak import KeycloakOpenID

from common.data_model.common import MeasureType, StationType, Station, Provenance, DataType

logger = logging.getLogger("pollution_v2.common.connector.common")


@dataclass
class Token:
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: Optional[str]
    token_type: str
    not_before_policy: str
    session_state: Optional[str]
    scope: List[str]
    created_at: datetime

    def to_repr(self) -> dict:
        return {
            "access_token": self.access_token,
            "expires_in": self.expires_in,
            "refresh_expires_in": self.refresh_expires_in,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "not-before-policy": self.not_before_policy,
            "session_state": self.session_state,
            "scope": " ".join(self.scope),
            "created_at": datetime.now().isoformat()
        }

    @staticmethod
    def from_repr(raw_data: dict) -> Token:
        return Token(
            access_token=raw_data["access_token"],
            expires_in=raw_data["expires_in"],
            refresh_expires_in=raw_data["refresh_expires_in"],
            refresh_token=raw_data.get("refresh_token"),
            token_type=raw_data["token_type"],
            not_before_policy=raw_data["not-before-policy"],
            session_state=raw_data.get("session_state"),
            scope=raw_data["scope"].split(" "),
            created_at=datetime.fromisoformat(raw_data["created_at"]) if raw_data.get("created_at") else datetime.now()
        )

    @property
    def is_expired(self) -> bool:
        """
        Check if the access token is expired.
        """
        return (self.created_at + timedelta(seconds=self.expires_in)) < datetime.now()

    @property
    def is_refresh_token_expired(self) -> bool:
        """
        Check if the refresh token is expired.
        """
        return (self.created_at + timedelta(seconds=self.refresh_expires_in)) < datetime.now()


class MaximumRetryExceeded(Exception):

    def __init__(self) -> None:
        super().__init__("Exceeded the maximum number of retry retries for the request.")


class ApiException(Exception):

    def __init__(self, message: str, code: int) -> None:
        super().__init__(f"Error in performing the request, server respond with [{code}], message: [{message}]")
        self.code = code
        self.message = message


class ODHBaseConnector(ABC, Generic[MeasureType, StationType]):

    def __init__(self,
                 base_reader_url: str,
                 base_writer_url: str,
                 station_type: str,
                 measure_types: List[str],
                 authentication_url: str,
                 username: Optional[str],
                 password: Optional[str],
                 client_id: Optional[str],
                 client_secret: Optional[str],
                 grant_type: List[str],
                 pagination_size: int,
                 max_post_batch_size: Optional[int],
                 requests_timeout: float,
                 requests_max_retries: int,
                 requests_sleep_time: float,
                 requests_retry_sleep_time: float,
                 period: Optional[int] = None):

        self._authentication_url = authentication_url
        self._base_reader_url = base_reader_url
        self._base_writer_url = base_writer_url
        self._station_type = station_type
        self._measure_types = measure_types
        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret
        self._grant_type = grant_type
        self._pagination_size = pagination_size
        self._max_batch_size = max_post_batch_size
        self._requests_timeout = requests_timeout
        self._requests_max_retries = requests_max_retries
        self._requests_sleep_time = requests_sleep_time
        self._requests_retry_sleep_time = requests_retry_sleep_time
        self._period = period

        self._keycloak_openid = KeycloakOpenID(server_url=self._authentication_url,
                                               client_id=self._client_id,
                                               realm_name="noi",
                                               client_secret_key=self._client_secret)

        self._token: Optional[Token] = None

    def _refresh_token(self) -> None:
        """
        Refresh current token or request a new one.
        """
        if not self._token or self._token.is_refresh_token_expired:
            logger.debug("Requesting new token")
            self._token = Token.from_repr(
                self._keycloak_openid.token(username=self._username, password=self._password,
                                            grant_type=self._grant_type)
            )
        elif self._token.refresh_token:
            logger.info("Refresh current access token")
            self._token = Token.from_repr(
                self._keycloak_openid.refresh_token(self._token.refresh_token)
            )

    def _get_token(self) -> Token:
        """
        Retrieve the access token or request a new one if needed.
        """
        if self._token is None or self._token.is_expired:
            self._refresh_token()
        return self._token

    @staticmethod
    def _get_authentication_header(token: Token) -> dict:
        """
        Get the authentication header to be used in the requests.
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"bearer {token.access_token}"
        }

    def _get_request(self, path: str, query_params: Optional[dict] = None) -> dict or list:
        """
        Perform a get request to the ODH.

        :param path:
        :param query_params:
        :return: A dictionary witch contains the decoded JSON body of the response
        :raise: JSONDecodeError if the body is not JSON encoded
        :raise: APIException if the server responds with a code different from 200
        :raise: MaximumRetryExceeded if the maximum re-tries are exceeded
        """
        token = self._get_token()

        if not query_params:
            query_params = {}

        call_counter = 0
        while call_counter <= self._requests_max_retries:
            call_counter += 1
            try:
                response = requests.get(
                    f"{self._base_reader_url}{path}",
                    headers=self._get_authentication_header(token),
                    params=query_params,
                    timeout=self._requests_timeout
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    raise ApiException(message=response.content.decode("utf-8"), code=response.status_code)
            except ApiException as e:
                raise e
            except Exception as e:
                logger.exception("Exception in getting data from ODH", exc_info=e)
                if call_counter <= self._requests_max_retries:
                    time.sleep(self._requests_retry_sleep_time)

        raise MaximumRetryExceeded()

    def _get_result_page(self, path: str, limit: int, offset: int, query_params: Optional[dict] = None) -> (
        list, int, int):
        """
        Request a result page from a paginated endpoint.

        :param path:
        :param limit:
        :param offset:
        :param query_params: Any additional query param
        :return: A tuple with the following structure (result list, current limit, current offset)
        """
        if not query_params:
            query_params = {}
        query_params.update({
            "limit": limit,
            "offset": offset
        })

        raw_data = self._get_request(path, query_params)

        if not isinstance(raw_data, dict):
            raise ValueError("Unable to handle the server response")

        try:
            return raw_data["data"], raw_data["limit"], raw_data["offset"]
        except KeyError as e:
            raise ValueError(f"Unable to build a result page from server response: {e}")

    def _get_result_list(self, path: str, query_params: Optional[dict] = None) -> List[dict]:
        """
        Request the result list from an endpoint.

        :param path:
        :param query_params: Any additional query param
        :return: The result list
        """
        limit = self._pagination_size
        offset = 0
        completed = False

        results: List[dict] = []

        while not completed:
            if limit == -1:
                logger.debug("Retrieving all elements")
            else:
                logger.debug(f"Retrieving page [{offset} - {offset + limit}]")

            new_results, limit, offset = self._get_result_page(path, limit=limit, offset=offset,
                                                               query_params=query_params)

            results.extend(new_results)
            if limit == -1:
                completed = True
            else:
                if len(new_results) == limit:
                    offset += limit
                    time.sleep(self._requests_sleep_time)
                else:
                    completed = True

        return results

    @staticmethod
    @abstractmethod
    def build_station(raw_station: dict) -> StationType:
        """
        Build a station from ODH representation.

        :param raw_station: A dictionary which contains the ODH json representation of a station
        :return:
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def build_measure(raw_measure: dict) -> MeasureType:
        """
        Build a measure from ODH representation.

        :param raw_measure: A dictionary which contains the ODH json representation of a measure
        :return:
        """
        raise NotImplementedError

    def get_station_list(self) -> list[StationType]:
        """
        Retrieve the list of all the available stations.
        """
        logger.info(f"Retrieving station list for type [{self._station_type}]")
        raw_stations = self._get_result_list(f"/v2/flat,node/{self._station_type}")

        logger.info(f"Retrieved [{len(raw_stations)}] stations")
        return [self.build_station(raw_station) for raw_station in raw_stations]

    def get_latest_measures(self, station: Optional[Station or str] = None,
                            period_to_include: int = None) -> List[MeasureType]:
        """
        Retrieve the last measure for the connector DataType.

        :param station: If set, it is possible to retrieve only the measures for the given station. It can be a string
                        representing the station code or a Station object.
        :param period_to_include: If set, it allows filtering including period; otherwise, no filter on period
        :return: The list of measures
        """

        where_conds = self.__build_where_conds(station, period_to_include)
        query_params = {}
        if len(where_conds) > 0:
            query_params["where"] = f'and({",".join(where_conds)})'

        logger.debug(f"Retrieving latest measures on [{type(self).__name__}] with where [{query_params['where']}]")

        raw_measures = self._get_result_list(
            path=f"/v2/flat,node/{self._station_type}/{','.join(self._measure_types)}/latest",
            query_params=query_params
        )

        return [self.build_measure(raw_measure) for raw_measure in raw_measures]

    def get_measures(self, from_date: datetime, to_date: datetime, station: Optional[Station or str] = None,
                     period_to_include: int = None) -> List[MeasureType]:
        """
        Retrieve the measures for the connector DataType in the given interval.

        :param from_date: The starting date of the interval
        :param to_date: The end date of the interval
        :param station: If set, it is possible to retrieve only the measures for the given station. It can be a string
                        representing the station code or a Station object.
        :param period_to_include: If set, it allows filtering including period; otherwise, no filter on period
        :return: the list of Measures
        """

        if period_to_include is None:
            period_to_include = self._period

        iso_from_date = from_date.isoformat(timespec="milliseconds")
        iso_to_date = to_date.isoformat(timespec="milliseconds")

        where_conds = self.__build_where_conds(station, period_to_include)
        query_params = {}
        if len(where_conds) > 0:
            query_params["where"] = f'and({",".join(where_conds)})'

        logger.debug(f"Retrieving measures on [{type(self).__name__}] from date [{iso_from_date}] "
                     f"to date [{iso_to_date}] with where [{query_params['where']}]")
        # TODO: remove
        print(f"Retrieving measures on [{type(self).__name__}] from date [{iso_from_date}] "
                     f"to date [{iso_to_date}] with where [{query_params['where']}]")

        raw_measures = self._get_result_list(
            path=f"/v2/flat,node/{self._station_type}/{','.join(self._measure_types)}/{iso_from_date}/{iso_to_date}",
            query_params=query_params
        )

        return [self.build_measure(raw_measure) for raw_measure in raw_measures]

    def __build_where_conds(self, station: Optional[Station or str] = None,
                            period_to_include: int = None) -> List[str]:

        where_condition = []
        if station:
            if isinstance(station, str):
                code = station
            elif isinstance(station, Station):
                code = station.code
            else:
                raise TypeError(f"Unable to handle a parameter of type [{type(station)}] as station")
            where_condition.append(f'scode.eq."{code}"')

        if period_to_include is not None:
            where_condition.append(f'mperiod.eq.{period_to_include}')

        return where_condition

    def _post_request(self, path: str, raw_data: dict or list,
                      query_params: Optional[dict] = None) -> str or dict or list:
        """
        Perform a post request to the ODH.

        :param path:
        :param query_params:
        :return: A dictionary witch contains the decoded JSON body of the response
        :raise: JSONDecodeError if the body is not JSON encoded
        :raise: APIException if the server responds with a code different from 201
        :raise: MaximumRetryExceeded if the maximum re-tries are exceeded
        """
        token = self._get_token()

        if not query_params:
            query_params = {}

        call_counter = 0
        while call_counter <= self._requests_max_retries:
            call_counter += 1
            try:
                logger.debug("posting...")
                logger.debug(f"where: {self._base_writer_url}{path}")
                logger.debug(f"what:  {raw_data}")
                logger.debug(f"with:  {self._get_authentication_header(token)}")
                logger.debug(f"param: {query_params}")
                response = requests.post(
                    f"{self._base_writer_url}{path}",
                    json=raw_data,
                    headers=self._get_authentication_header(token),
                    params=query_params,
                    timeout=self._requests_timeout
                )
                if response.status_code in [200, 201]:
                    try:  # ODH seems that id not returning a json for post requests but a string
                        logger.debug(f"Response code is {response.status_code}, response is {response.json()}")
                        return response.json()
                    except requests.exceptions.JSONDecodeError:
                        logger.debug(f"Response code is {response.status_code}, error decoding json: {response.text}")
                        return response.text
                else:
                    logger.debug(f"Response code is {response.status_code}, considered as error!")
                    raise ApiException(message=response.content.decode("utf-8"), code=response.status_code)
            except ApiException as e:
                logger.exception("API Exception in getting data from ODH", exc_info=e)
                raise e
            except Exception as e:
                logger.exception("Exception in getting data from ODH", exc_info=e)
                if call_counter <= self._requests_max_retries:
                    time.sleep(self._requests_retry_sleep_time)

        raise MaximumRetryExceeded()

    def post_provenance(self, provenance: Provenance) -> str:
        """
        Create a provenance (if it is already present it will not be duplicated) and get its id.

        :param provenance: The provenance to be created.
        :return: the id of the created provenance.
        """
        logger.info("Creating provenance")
        provenance_id = self._post_request("/json/provenance", provenance.to_odh_repr())
        return provenance_id

    def _post_data_type_batch(self, data_types: List[DataType], provenance: Provenance) -> None:
        """
        Create a batch of data types (if a data type with the same name is already present it will be updated).

        :param data_types: The data types to be created.
        :param provenance: The provenance related to the data type to be created.
        """
        logger.debug("Creating a batch of data types")
        self._post_request("/json/syncDataTypes",
                           [data_type.to_odh_repr() for data_type in data_types],
                           query_params={
                               "stationType": self._station_type,
                               "prn": provenance.data_collector,
                               "prv": provenance.data_collector_version
                           })

    def post_data_types(self, data_types: List[DataType], provenance: Provenance) -> None:
        """
        Create data types (if a data type with the same name is already present it will be updated).

        :param data_types: The data types to be created.
        :param provenance: The provenance related to the data type to be created.
        """
        logger.info("Creating data types")
        if not self._max_batch_size or (self._max_batch_size and self._max_batch_size >= len(data_types)):
            self._post_data_type_batch(data_types, provenance)
        else:
            for index in range(len(data_types) // self._max_batch_size + 1):
                if index < len(data_types) // self._max_batch_size:
                    self._post_data_type_batch(
                        data_types[index * self._max_batch_size: (index + 1) * self._max_batch_size], provenance)
                else:
                    if len(data_types) > index * self._max_batch_size:
                        self._post_data_type_batch(data_types[index * self._max_batch_size:], provenance)

    def _post_measure_batch(self, measures: List[MeasureType]) -> None:
        """
        Create a batch of measures (if a measure is already present with a newer valid time it will be ignored).

        :param measures: The measures to be created.
        """

        # This method accepts the measures and then subdivides them by provenance id, station code and data type
        # {
        #   <provenance id>: {
        #     <station code>: {
        #       <data type>: [measures list]
        #     }
        #   }
        # }

        logger.debug("Creating a batch of measures")
        measures_dict = {}
        for measure in measures:
            if measure.provenance.provenance_id not in measures_dict:
                measures_dict[measure.provenance.provenance_id] = {}

            if measure.station.code not in measures_dict[measure.provenance.provenance_id]:
                measures_dict[measure.provenance.provenance_id][measure.station.code] = {}

            if measure.data_type.name not in measures_dict[measure.provenance.provenance_id][measure.station.code]:
                measures_dict[measure.provenance.provenance_id][measure.station.code][measure.data_type.name] = [
                    measure]
            else:
                measures_dict[measure.provenance.provenance_id][measure.station.code][measure.data_type.name].append(
                    measure)

        if len(measures_dict.keys()) > 1:
            logger.error("Measures have more than one provenance")

        for provenance_id in measures_dict:
            data_map = {
                "name": "(default)",
                "branch": {},
                "data": [],
                "provenance": provenance_id
            }
            for station_code in measures_dict[provenance_id]:
                data_map["branch"][station_code] = {
                    "name": "(default)",
                    "branch": {},
                    "data": []
                }
                for data_type_name in measures_dict[provenance_id][station_code]:
                    data_map["branch"][station_code]["branch"][data_type_name] = {
                        "name": "(default)",
                        "branch": {},
                        # Send data to ODH in chronological order
                        "data": [data_point.to_odh_repr() for data_point in
                                 measures_dict[provenance_id][station_code][data_type_name]]
                    }

            self._post_request(f"/json/pushRecords/{self._station_type}", data_map)

    def post_measures(self, measures: List[MeasureType]) -> None:
        """
        Create measures (if a measure is already present with a newer valid time it will be ignored).

        :param measures: The measures to be created.
        """
        logger.info("Creating measures")
        measures.sort(key=lambda x: x.valid_time)  # Send data to ODH in chronological order
        if not self._max_batch_size or (self._max_batch_size and self._max_batch_size >= len(measures)):
            self._post_measure_batch(measures)
        else:
            for index in range(len(measures) // self._max_batch_size + 1):
                if index < len(measures) // self._max_batch_size:
                    self._post_measure_batch(measures[index * self._max_batch_size: (index + 1) * self._max_batch_size])
                else:
                    if len(measures) > index * self._max_batch_size:
                        self._post_measure_batch(measures[index * self._max_batch_size:])
