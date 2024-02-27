# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import itertools
import logging
from datetime import datetime
from typing import List

from common.connector.collector import ConnectorCollector
from common.data_model import TrafficMeasureCollection, TrafficSensorStation, StationLatestMeasure
from common.settings import ODH_MINIMUM_STARTING_DATE

logger = logging.getLogger("common.manager.traffic_station")


class TrafficStationManager:

    def __init__(self, connector_collector: ConnectorCollector):
        self._connector_collector = connector_collector
        self._traffic_stations: List[TrafficSensorStation] = []

    def get_traffic_stations_from_cache(self) -> List[TrafficSensorStation]:
        if len(self._traffic_stations) == 0:
            logger.info("Retrieving station list from ODH")
            self._traffic_stations = self._get_station_list()
        return self._traffic_stations

    def get_all_latest_measures(self) -> List[StationLatestMeasure]:
        """
        Returns a list of stations with its latest measure date.

        :return: List of stations with its latest measure date.
        """
        all_measures = self._connector_collector.traffic.get_latest_measures()

        grouped = {}
        for station_code, values in itertools.groupby(all_measures, lambda m: m.station.code):
            tmp = list(values)
            if len(tmp) > 0:
                grouped[station_code] = tmp

        res = []
        for key, value in grouped.items():
            res.append(StationLatestMeasure(key, max(list(map(lambda m: m.valid_time, value)),
                                                     default=ODH_MINIMUM_STARTING_DATE)))

        return res

    def _get_station_list(self) -> List[TrafficSensorStation]:
        """
        Retrieve the list of all the available stations.
        """
        return self._connector_collector.traffic.get_station_list()

    def _download_traffic_data(self,
                               from_date: datetime,
                               to_date: datetime,
                               traffic_station: TrafficSensorStation
                               ) -> TrafficMeasureCollection:
        """
        Download traffic data measures in the given interval.

        :param from_date: Traffic measures before this date are discarded if there isn't any latest pollution measure available.
        :param to_date: Traffic measure after this date are discarded.
        :return: The resulting TrafficMeasureCollection containing the traffic data.
        """

        return TrafficMeasureCollection(measures=self._connector_collector.traffic.get_measures(from_date=from_date, to_date=to_date, station=traffic_station))
