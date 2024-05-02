# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

from common.cache.computation_checkpoint import ComputationCheckpointCache, ComputationCheckpoint
from common.connector.collector import ConnectorCollector
from common.connector.common import ODHBaseConnector
from common.data_model import TrafficSensorStation
from common.data_model.common import MeasureType, Provenance, DataType, MeasureCollection, Measure
from common.data_model.entry import GenericEntry
from common.settings import ODH_MINIMUM_STARTING_DATE, DEFAULT_TIMEZONE

logger = logging.getLogger("pollution_v2.common.manager.traffic_station")


def _get_stations_on_logs(stations: List[TrafficSensorStation]):
    return (f"[{', '.join([station.code for station in (stations[:5] if len(stations) > 5 else stations)])}"
            f"{' and more (' + str(len(stations)) + ')' if len(stations) > 5 else ''}]")


class TrafficStationManager(ABC):
    """
    Abstract class generalising traffic managers, in charge of computing the data given the traffic data.
    """

    def __init__(self, connector_collector: ConnectorCollector, provenance: Provenance,
                 checkpoint_cache: Optional[ComputationCheckpointCache] = None):
        self._checkpoint_cache = checkpoint_cache
        self._connector_collector = connector_collector
        self._provenance = provenance
        self._traffic_stations: List[TrafficSensorStation] = []
        self._create_data_types = True

    @abstractmethod
    def _get_manager_code(self) -> str:
        pass

    @abstractmethod
    def get_output_connector(self) -> ODHBaseConnector:
        """
        Returns the colletor of the data in charge of the implementing manager class.
        """
        pass

    @abstractmethod
    def get_input_connector(self) -> ODHBaseConnector:
        """
        Returns the collector for retrieving input data for computing and the dates useful to determine processing
        interval for the implementing manager class.
        """
        pass

    @abstractmethod
    def _get_data_types(self) -> List[DataType]:
        """
        Returns the data types specific for the implementing manager class.
        """
        pass

    @abstractmethod
    def _build_from_entries(self, input_entries: List[GenericEntry]) -> MeasureCollection:
        """
        Builds the measure collection given the entries for the implementing manager class.

        :param input_entries: manager specific class entries.
        """
        pass

    @abstractmethod
    def _download_data_and_compute(self, start_date: datetime, to_date: datetime,
                                   stations: List[TrafficSensorStation]) -> List[GenericEntry]:
        pass

    def _get_latest_date(self, connector: ODHBaseConnector, stations: List[TrafficSensorStation]) -> datetime:
        latest_date_across_stations = None
        for station in stations:
            measures = connector.get_latest_measures(station=station)
            latest_date = max(list(map(lambda m: m.valid_time, measures)),
                              default=DEFAULT_TIMEZONE.localize(ODH_MINIMUM_STARTING_DATE))
            if latest_date_across_stations is None or latest_date > latest_date_across_stations:
                latest_date_across_stations = latest_date
        return latest_date_across_stations

    def get_starting_date(self, connector: ODHBaseConnector, stations: List[TrafficSensorStation],
                          min_from_date: datetime) -> datetime:
        """
        Returns the starting date for further processing, even managing some fallback values if necessary.

        :param connector: The connector used to retrieve data.
        :param stations: The list of traffic stations to query.
        :param min_from_date: The minimum date to start from.
        :return: Computation starting date.
        """

        logger.info(f"Looking for latest measures available on [{type(connector).__name__}] "
                    f"for {_get_stations_on_logs(stations)} ")
        from_date_across_stations = None
        for station in stations:
            latest_measure = self.__get_latest_measure(connector, station)
            if latest_measure is None:
                logger.info(f"No measures available on [{type(connector).__name__}] for [{station.code}]")
                if self._checkpoint_cache is not None:
                    logger.info(
                        f"Looking on checkpoints on [{type(connector).__name__}] for [{station.code}]")
                    checkpoint = self._checkpoint_cache.get(
                        ComputationCheckpoint.get_id_for_station(station, self._get_manager_code()))
                    if checkpoint is not None:
                        logger.info(f"Using checkpoint date [{checkpoint.checkpoint_dt}] as starting date "
                                    f"for [{station.code}]")
                        from_date = checkpoint.checkpoint_dt
                    else:
                        # If there isn't any latest measure available,
                        # the min_from_date is used as starting date for the batch
                        logger.info(f"No checkpoint, using min date [{min_from_date}] "
                                    f"as starting date for [{station.code}]")
                        from_date = min_from_date
                else:
                    # If there isn't any latest measure available,
                    # the min_from_date is used as starting date for the batch
                    logger.info(f"No measures, using min date [{min_from_date}] "
                                f"as starting date for [{station.code}]")
                    from_date = min_from_date
            else:
                logger.info(f"Measures found, using min date [{latest_measure.valid_time}] "
                            f"as starting date for [{station.code}]")
                from_date = latest_measure.valid_time

            if from_date.tzinfo is None:
                from_date = DEFAULT_TIMEZONE.localize(from_date)

            if min_from_date.tzinfo is None:
                min_from_date = DEFAULT_TIMEZONE.localize(min_from_date)

            if from_date.microsecond:
                from_date = from_date.replace(microsecond=0)

            if from_date < min_from_date:
                logger.warning(f"Latest measure date is [{from_date.isoformat()}] as candidate starting date, "
                               f"but it's before the minimum starting date [{min_from_date.isoformat()}]; "
                               f"using [{min_from_date.isoformat()}]")
                from_date = min_from_date
            elif from_date > min_from_date:
                logger.info(f"Using latest measure date [{from_date.isoformat()}] as starting date, "
                            f"which is after the minimum starting date [{min_from_date.isoformat()}]")

            if from_date_across_stations is None or from_date < from_date_across_stations:
                from_date_across_stations = from_date

        return from_date_across_stations

    def __get_latest_measure(self, connector: ODHBaseConnector,
                             station: Optional[TrafficSensorStation]) -> Optional[Measure]:
        """
        Retrieve the latest measure for a given station. It will be the oldest one among all the measure types
        (for pollution, CO-emissions, CO2-emissions, ...) even though should be the same for all the types.

        :param station: The station for which retrieve the latest measure.
        :return: The latest measure for a given station.
        """
        latest_measures = connector.get_latest_measures(station)
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
            self._traffic_stations = self.__get_station_list()

        return self._traffic_stations

    def __get_station_list(self) -> List[TrafficSensorStation]:
        """
        Retrieve the list of all the available stations.
        """
        return self._connector_collector.traffic.get_station_list()

    def _download_traffic_data(self,
                               from_date: datetime,
                               to_date: datetime,
                               stations: List[TrafficSensorStation]
                               ) -> List[MeasureType]:
        """
        Download traffic data measures in the given interval.

        :param from_date: Traffic measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Traffic measure after this date are discarded.
        :return: The resulting TrafficMeasureCollection containing the traffic data.
        """

        res = []
        for station in stations:
            res.extend(self._connector_collector.traffic.get_measures(from_date=from_date, to_date=to_date,
                                                                      station=station))

        return res

    def _upload_data(self, input_entries: List[GenericEntry]) -> None:
        """
        Upload the input data on ODH.
        If a data is already present it will be not overridden and
        data before the last measures are not accepted by the ODH.

        :param input_entries: The entries to be processed.
        """

        logger.info(f"Posting provenance {self._provenance}")
        if not self._provenance.provenance_id:
            self._provenance.provenance_id = self.get_output_connector().post_provenance(self._provenance)

        logger.info(f"Posting data types {self._get_data_types()}")
        if self._create_data_types:
            self.get_output_connector().post_data_types(self._get_data_types(), self._provenance)

        data = self._build_from_entries(input_entries)
        logger.info(f"Posting measures {len(data.measures)}")
        self.get_output_connector().post_measures(data.measures)

    def run_computation(self,
                        stations: List[TrafficSensorStation],
                        min_from_date: datetime,
                        max_to_date: datetime,
                        batch_size: int) -> None:
        """
        Start the computation of a batch of data measures on a specific station.
        As starting date for the  batch is used the latest measure available on the ODH,
        if no measures are available min_from_date is used.

        :param stations: List of stations to process.
        :param min_from_date: Traffic measures before this date are discarded if no measures are available.
        :param max_to_date: Ending date for interval; measures after this date are discarded.
        :param batch_size: Number of days to be processed as maximum span.
        """

        logger.info(f"Determining computation interval for {_get_stations_on_logs(stations)} "
                    f"between [{min_from_date}] and [{max_to_date}]")

        start_date = self.get_starting_date(self.get_output_connector(), stations, min_from_date)

        # Detect inactive stations:
        # If we're about to request more than one window of measurements, do a check first if there even is any new data
        if (max_to_date - start_date).days > batch_size:
            latest_measurement_date = self._get_latest_date(self.get_input_connector(), stations)
            # traffic data request range end is the latest measurement
            # For inactive stations, this latest measurement date will be < start_date,
            # thus no further requests will be made. In general, it makes no sense to ask for data
            # beyond the latest measurement, if we already know which date that is.
            logger.info(f"Stations {_get_stations_on_logs(stations)} has a large elaboration range "
                        f"as latest measurement date is {latest_measurement_date}")
            max_to_date = min(max_to_date, latest_measurement_date)

        to_date = start_date

        if start_date == max_to_date:
            logger.info(f"Not computing data for stations {_get_stations_on_logs(stations)} in interval "
                        f"[{start_date.isoformat()} - {to_date.isoformat()}] (no timespan)")
        elif start_date < max_to_date:
            to_date = to_date + timedelta(days=batch_size)
            if to_date > max_to_date:
                to_date = max_to_date

            logger.info(f"Computing data for stations {_get_stations_on_logs(stations)} in interval "
                        f"[{start_date.isoformat()} - {to_date.isoformat()}]")

            try:
                entries = self._download_data_and_compute(start_date, to_date, stations)
                self._upload_data(entries)
            except Exception as e:
                logger.exception(f"Unable to compute data from stations {_get_stations_on_logs(stations)} in the "
                                 f"interval [{start_date.isoformat()}] - [{to_date.isoformat()}]", exc_info=e)

            if self._checkpoint_cache is not None:
                for station in stations:
                    self._checkpoint_cache.set(
                        ComputationCheckpoint(
                            station_code=station.code,
                            checkpoint_dt=to_date,
                            manager_code=self._get_manager_code()
                        )
                    )
        else:
            logger.info(f"Nothing to process for stations {_get_stations_on_logs(stations)} in interval "
                        f"[{start_date} - {to_date}]")

    def run_computation_and_upload_results(self,
                                           min_from_date: datetime,
                                           max_to_date: datetime,
                                           batch_size: int) -> None:
        """
        Watch-out! Used only from main_*!

        Start the computation of a batch of data measures. As starting date for the batch is used the latest
        measure available on the ODH, if no measures are available min_from_date is used.

        :param min_from_date: Traffic measures before this date are discarded if no measures are available.
        :param max_to_date: Traffic measure after this date are discarded.
        :param batch_size: Number of days to be processed as maximum span.
        """

        if min_from_date.tzinfo is None:
            min_from_date = DEFAULT_TIMEZONE.localize(min_from_date)

        if max_to_date.tzinfo is None:
            max_to_date = DEFAULT_TIMEZONE.localize(max_to_date)

        computation_start_dt = datetime.now()

        stations = self.get_traffic_stations_from_cache()
        stations_with_km = [station for station in stations if station.km > 0]
        logger.info(f"Stations filtered on having km defined, resulting {len(stations_with_km)} "
                    f"elements (starting from {len(stations)})")

        self.run_computation(stations_with_km, min_from_date, max_to_date, batch_size)

        computation_end_dt = datetime.now()
        logger.info(f"Completed computation in [{(computation_end_dt - computation_start_dt).seconds}]")
