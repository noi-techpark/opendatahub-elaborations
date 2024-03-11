# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import itertools
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional, Generic

from common.cache.computation_checkpoint import ComputationCheckpointCache, ComputationCheckpoint
from common.connector.collector import ConnectorCollector
from common.connector.common import ODHBaseConnector
from common.data_model import TrafficMeasureCollection, TrafficSensorStation, StationLatestMeasure, Measure
from common.data_model.common import Provenance, DataType
from common.data_model.entry import GenericEntry
from common.model.model import GenericModel
from common.settings import ODH_MINIMUM_STARTING_DATE, DEFAULT_TIMEZONE, ODH_COMPUTATION_BATCH_SIZE

logger = logging.getLogger("pollution_v2.common.manager.traffic_station")


def _get_latest_date(connector: ODHBaseConnector, traffic_station: TrafficSensorStation) -> datetime:
    """
    Compute the output data given the input data.

    :param connector: The connector to use to retrieve data.
    :param traffic_station: The traffic station to work on.
    :return: The output entries.
    """
    measures = connector.get_latest_measures(station=traffic_station)
    return max(list(map(lambda m: m.valid_time, measures)), default=ODH_MINIMUM_STARTING_DATE)


class TrafficStationManager(ABC):
    """
    Abstract manager for interactions on traffic stations
    """

    def __init__(self, connector_collector: ConnectorCollector, provenance: Provenance,
                 checkpoint_cache: Optional[ComputationCheckpointCache] = None):
        self._checkpoint_cache = checkpoint_cache
        self._connector_collector = connector_collector
        self._provenance = provenance
        self._traffic_stations: List[TrafficSensorStation] = []
        self._create_data_types = True

    @abstractmethod
    def _get_model(self) -> GenericModel:
        pass

    @abstractmethod
    def _get_main_collector(self) -> ODHBaseConnector:
        pass

    @abstractmethod
    def _get_latest_date_collector(self) -> ODHBaseConnector:
        pass

    @abstractmethod
    def _get_data_types(self) -> List[DataType]:
        pass

    @abstractmethod
    def _build_from_entries(self, input_entries: List[GenericEntry]):
        pass

    def _compute_data(self, input_data: TrafficMeasureCollection) -> List[GenericEntry]:
        """
        Compute the output data given the input data.

        :param input_data: The input data.
        :return: The output entries.
        """
        model = self._get_model()
        return model.compute_data(input_data)

    def _get_starting_date(self, connector: ODHBaseConnector, traffic_station: TrafficSensorStation,
                           min_from_date: datetime) -> datetime:
        latest_measure = self._get_latest_measure_by_connector(connector, traffic_station)
        if latest_measure is None:
            logger.info(f"No measures available for station [{traffic_station.code}]")
            if self._checkpoint_cache is not None:
                checkpoint = self._checkpoint_cache.get(ComputationCheckpoint.get_id_for_station(traffic_station))
                if checkpoint is not None:
                    logger.info(f"Using checkpoint date [{checkpoint.checkpoint_dt.isoformat()}] "
                                f"as starting date for station [{traffic_station.code}]")
                    from_date = checkpoint.checkpoint_dt
                else:
                    # If there isn't any latest measure available,
                    # the min_from_date is used as starting date for the batch
                    from_date = min_from_date
            else:
                # If there isn't any latest measure available, the min_from_date is used as starting date for the batch
                from_date = min_from_date
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

    def _get_latest_measure_by_connector(self, connector: ODHBaseConnector,
                                         traffic_station: TrafficSensorStation) -> Optional[Measure]:
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
        """
        Returns a list of stations from cache.

        :return: List of stations from cache.
        """
        if len(self._traffic_stations) == 0:
            logger.info("Retrieving station list from ODH")
            self._traffic_stations = self._get_station_list()
        return self._traffic_stations

    def get_all_latest_measures(self) -> List[StationLatestMeasure]:
        """
        Returns a list of stations with its latest measure date.

        :return: List of stations with its latest measure date.
        """
        all_measures = self._get_main_collector().get_latest_measures()

        grouped = {}
        for station_code, values in itertools.groupby(all_measures, lambda m: m.station.code):
            tmp = list(values)
            if len(tmp) > 0:
                grouped[station_code] = tmp

        res = []
        for key, value in grouped.items():
            logger.debug(f"Latest date for {key} is {max(list(map(lambda m: m.valid_time, value)),  default=ODH_MINIMUM_STARTING_DATE)}")
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

        :param from_date: Traffic measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Traffic measure after this date are discarded.
        :return: The resulting TrafficMeasureCollection containing the traffic data.
        """

        return TrafficMeasureCollection(measures=self._connector_collector.traffic.get_measures(from_date=from_date,
                                                                                                to_date=to_date,
                                                                                                station=traffic_station))

    def _upload_data(self, input_entries: List[GenericEntry]) -> None:
        """
        Upload the input data on ODH.
        If a data is already present it will be not overridden and
        data before the last measures are not accepted by the ODH

        :param input_entries: The input entries.
        """

        logger.debug(f"Posting provenance {self._provenance}")
        if not self._provenance.provenance_id:
            self._provenance.provenance_id = self._get_main_collector().post_provenance(self._provenance)

        logger.debug(f"Posting data types {self._get_data_types()}")
        if self._create_data_types:
            self._get_main_collector().post_data_types(self._get_data_types(), self._provenance)

        data = self._build_from_entries(input_entries)
        logger.debug(f"Posting measures {len(data.measures)}")
        self._get_main_collector().post_measures(data.measures)

    def run_computation_for_station(self,
                                    traffic_station: TrafficSensorStation,
                                    min_from_date: datetime,
                                    max_to_date: datetime) -> None:
        """
        Runs the requested computation for the given station.

        :param traffic_station: Traffic station working on.
        :param min_from_date: Starting date for interval.
        :param max_to_date: Ending date for interval.
        """
        start_date = self._get_starting_date(self._get_main_collector(), traffic_station, min_from_date)

        # Detect inactive stations:
        # If we're about to request more than one window of measurements, do a check first if there even is any new data
        if (max_to_date - start_date).days > ODH_COMPUTATION_BATCH_SIZE:
            latest_measurement_date = _get_latest_date(self._get_latest_date_collector(), traffic_station)
            # traffic data request range end is the latest measurement
            # For inactive stations, this latest measurement date will be < start_date,
            # thus no further requests will be made. In general, it makes no sense to ask for data beyond
            # the latest measurement, if we already know which date that is.
            logger.info(f"Station [{traffic_station.code}] has a large elaboration range. "
                        f"Latest measurement date: {latest_measurement_date}")
            max_to_date = min(max_to_date, latest_measurement_date)

        to_date = start_date

        if start_date < max_to_date:
            to_date = to_date + timedelta(days=ODH_COMPUTATION_BATCH_SIZE)
            if to_date > max_to_date:
                to_date = max_to_date

            logger.info(f"Computing data for station [{traffic_station}] in interval "
                        f"[{start_date.isoformat()} - {to_date.isoformat()}]")

            traffic_data = []
            try:
                traffic_data = self._download_traffic_data(start_date, to_date, traffic_station)
            except Exception as e:
                logger.exception(
                    f"Unable to download traffic data for station [{traffic_station}] "
                    f"in the interval [{start_date.isoformat()}] - [{to_date.isoformat()}]",
                    exc_info=e)

            if traffic_data:
                try:
                    computed_entries = self._compute_data(traffic_data)
                    self._upload_data(computed_entries)
                except Exception as e:
                    logger.exception(f"Unable to compute data from station [{traffic_station}] in the interval "
                                     f"[{start_date.isoformat()}] - [{to_date.isoformat()}]", exc_info=e)

                if self._checkpoint_cache is not None:
                    self._checkpoint_cache.set(
                        ComputationCheckpoint(
                            station_code=traffic_station.code,
                            checkpoint_dt=to_date
                        )
                    )

    def run_computation_and_upload_results(self,
                                           min_from_date: datetime,
                                           max_to_date: datetime
                                           ) -> None:
        """
        Start the computation of a batch of data measures. As starting date for the batch is used the latest
        measure available on the ODH, if no measures are available min_from_date is used.

        :param min_from_date: Traffic measures before this date are discarded if no measures are available.
        :param max_to_date: Traffic measure after this date are discarded.
        """

        if min_from_date.tzinfo is None:
            min_from_date = DEFAULT_TIMEZONE.localize(min_from_date)

        if max_to_date.tzinfo is None:
            max_to_date = DEFAULT_TIMEZONE.localize(max_to_date)

        computation_start_dt = datetime.now()

        for traffic_station in self.get_traffic_stations_from_cache():
            self.run_computation_for_station(traffic_station, min_from_date, max_to_date)

        computation_end_dt = datetime.now()
        logger.info(f"Completed computation in [{(computation_end_dt - computation_start_dt).seconds}]")
