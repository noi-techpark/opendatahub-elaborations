# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from typing import Optional, List

from common.connector.common import ODHBaseConnector
from common.data_model import PollutionDispersalMeasure, Station, TrafficSensorStation
from common.settings import PERIOD_1HOUR

logger = logging.getLogger("pollution_v2.common.connector.pollution_dispersal")

class PollutionDispersalODHConnector(ODHBaseConnector[PollutionDispersalMeasure, Station]):

    def __init__(self,
                 base_reader_url: str,
                 base_writer_url: str,
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
                 requests_retry_sleep_time: float) -> None:

        self.station_type = "EnvironmentStation"
        measure_types = list([dt.name for dt in PollutionDispersalMeasure.get_data_types()])
        period = PERIOD_1HOUR


        super().__init__(base_reader_url,
                         base_writer_url,
                         self.station_type,
                         measure_types,
                         authentication_url,
                         username,
                         password,
                         client_id,
                         client_secret,
                         grant_type,
                         pagination_size,
                         max_post_batch_size,
                         requests_timeout,
                         requests_max_retries,
                         requests_sleep_time,
                         requests_retry_sleep_time,
                         period)

    @staticmethod
    def build_station(raw_station: dict) -> Station:
        return Station.from_odh_repr(raw_station)

    @staticmethod
    def build_measure(raw_measure: dict) -> PollutionDispersalMeasure:
        return PollutionDispersalMeasure.from_odh_repr(raw_measure)

    def _build_where_conds(self, station: Optional[Station or str] = None,
                            period_to_include: int = None, conditions: list[str] = None) -> List[str]:
        where_condition = []
        if station:
            if isinstance(station, str):
                code = station
            elif isinstance(station, TrafficSensorStation):
                code = station.id_stazione
            elif isinstance(station, Station):
                code = station.code
            else:
                raise TypeError(f"Unable to handle a parameter of type [{type(station)}] as station")
            where_condition.append(f'smetadata.traffic_station_code.eq."{code}"')

        if period_to_include is not None:
            where_condition.append(f'mperiod.eq.{period_to_include}')

        if conditions is not None:
            where_condition.extend(conditions)

        return where_condition
