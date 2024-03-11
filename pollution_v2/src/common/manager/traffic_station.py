# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import itertools
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from common.connector.collector import ConnectorCollector
from common.connector.common import ODHBaseConnector
from common.data_model import TrafficMeasureCollection, TrafficSensorStation, StationLatestMeasure, Measure
from common.settings import ODH_MINIMUM_STARTING_DATE, DEFAULT_TIMEZONE
from pollution_connector.cache.computation_checkpoint import ComputationCheckpoint, ComputationCheckpointCache

logger = logging.getLogger("common.manager.traffic_station")


class TrafficStationManager(ABC):

    def __init__(self, connector_collector: ConnectorCollector, checkpoint_cache: Optional[ComputationCheckpointCache] = None):
        self._checkpoint_cache = checkpoint_cache
        self._connector_collector = connector_collector
        self._traffic_stations: List[TrafficSensorStation] = []

    def _get_latest_date(self, connector: ODHBaseConnector, traffic_station: TrafficSensorStation) -> datetime:
        measures = connector.get_latest_measures(station=traffic_station)
        return max(list(map(lambda m: m.valid_time, measures)), default=ODH_MINIMUM_STARTING_DATE)

    def _get_starting_date(self, connector: ODHBaseConnector, traffic_station: TrafficSensorStation, min_from_date: datetime) -> datetime:
        latest_measure = self._get_latest_measure_by_connector(connector, traffic_station)
        if latest_measure is None:
            logger.info(f"No measures available for station [{traffic_station.code}]")
            if self._checkpoint_cache is not None:
                checkpoint = self._checkpoint_cache.get(ComputationCheckpoint.get_id_for_station(traffic_station))
                if checkpoint is not None:
                    logger.info(f"Using checkpoint date [{checkpoint.checkpoint_dt.isoformat()}] as starting date for station [{traffic_station.code}]")
                    from_date = checkpoint.checkpoint_dt
                else:
                    from_date = min_from_date  # If there isn't any latest measure available, the min_from_date is used as starting date for the batch
            else:
                from_date = min_from_date  # If there isn't any latest measure available, the min_from_date is used as starting date for the batch
        else:
            from_date = latest_measure.valid_time

        if from_date.tzinfo is None:
            from_date = DEFAULT_TIMEZONE.localize(from_date)

        if from_date.microsecond:
            from_date = from_date.replace(microsecond=0)

        if from_date < min_from_date:
            logger.warning(f"Using latest measure date [{from_date.isoformat()}] as starting date, "
                           f"but it's before the minimum starting date [{min_from_date.isoformat()}]")
        elif from_date > min_from_date:
            logger.warning(f"Using latest measure date [{from_date.isoformat()}] as starting date, "
                           f"which is after the minimum starting date [{min_from_date.isoformat()}]")

        return from_date

    def _get_latest_measure_by_connector(self, connector: ODHBaseConnector, traffic_station: TrafficSensorStation) -> Optional[Measure]:
        """
        Retrieve the latest measure for a given station. It will be the oldest one among all the measure types
        even though should be the same for all the types.

        :param traffic_station: The station for which retrieve the latest measure.
        :return: The latest measure for a given station.
        """
        latest_measures = connector.get_latest_measures(traffic_station)
        if latest_measures:
            self._create_data_types = False
            latest_measures.sort(key=lambda x: x.valid_time)
            return latest_measures[0]

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
