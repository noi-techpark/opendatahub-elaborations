# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from common.cache.computation_checkpoint import ComputationCheckpointCache, ComputationCheckpoint
from common.connector.collector import ConnectorCollector
from common.connector.common import ODHBaseConnector
from common.data_model import TrafficSensorStation, DataType
from common.data_model.common import MeasureType, Provenance, Measure
from common.data_model.entry import GenericEntry
from common.manager.station import StationManager
from common.settings import ODH_MINIMUM_STARTING_DATE, DEFAULT_TIMEZONE, get_now

logger = logging.getLogger("pollution_v2.common.manager.traffic_station")


def _get_stations_on_logs(stations: List[TrafficSensorStation]):
    return (f"[{', '.join([station.code for station in (stations[:5] if len(stations) > 5 else stations)])}"
            f"{' and more (' + str(len(stations)) + ')' if len(stations) > 5 else ''}]")


class TrafficStationManager(StationManager, ABC):
    """
    Abstract class generalising traffic managers, in charge of computing the data given the traffic data.
    """

    def __init__(self, connector_collector: ConnectorCollector, provenance: Provenance,
                 checkpoint_cache: Optional[ComputationCheckpointCache] = None):
        super().__init__(connector_collector, provenance, checkpoint_cache)
        self._traffic_stations: List[TrafficSensorStation] = []
        self.station_list_connector = connector_collector.traffic

    @abstractmethod
    def _get_manager_code(self) -> str:
        pass

    @abstractmethod
    def _download_data_and_compute(self, start_date: datetime, to_date: datetime,
                                   stations: List[TrafficSensorStation]) -> List[GenericEntry]:
        pass

    def get_input_data_types(self) -> Optional[List[MeasureType]]:
        """
        Returns the data types specific to filter the input data when retrieving the starting date.
        If None is returned, no filter is applied.
        """
        return None

    def _get_latest_date(self, connector: ODHBaseConnector, stations: List[TrafficSensorStation]) -> datetime:
        latest_date_across_stations = None
        for station in stations:
            req_data_types = None
            input_data_types = self.get_input_data_types()
            if input_data_types:
                req_data_types = list(map(lambda x: x.name, input_data_types))
            measures = connector.get_latest_measures(station=station, data_types=req_data_types)
            latest_date = max(list(map(lambda m: m.valid_time, measures)),
                              default=ODH_MINIMUM_STARTING_DATE)
            if latest_date_across_stations is None or latest_date > latest_date_across_stations:
                latest_date_across_stations = latest_date
        return latest_date_across_stations

    def get_starting_date(self, output_connector: ODHBaseConnector, input_connector: ODHBaseConnector | None,
                          stations: List[TrafficSensorStation], min_from_date: datetime, batch_size: int,
                          keep_looking_for_input_data: bool, output_data_types: list[DataType] = None) -> datetime:
        """
        Returns the starting date for further processing, even managing some fallback values if necessary.

        :param output_connector: The connector used to retrieve latest previously processed data.
        :param input_connector: The connector used to retrieve the next data ready to be processed.
        :param stations: The list of traffic stations to query.
        :param min_from_date: The minimum date to start from.
        :param batch_size: The size of the batch (in days) to be extracted.
        :param keep_looking_for_input_data: If input data has no data, updates checkpoint and goes on looking for data:
                                            Useful to find the first traffic data for a station on validation
                                            To be avoided when there are no validation data on pollution (wait for them)
        :param output_data_types: The data types to filter the output measures.
        :return: Computation starting date.
        """

        if stations and len(stations) == 1:
            logger.info(f"[{stations[0].code}] Looking for latest measures available on "
                        f"[{type(output_connector).__name__}]")
        else:
            logger.info(f"Looking for latest measures available on [{type(output_connector).__name__}] "
                        f"for {_get_stations_on_logs(stations)} ")
        from_date_across_stations = None
        for station in stations:
            from_date = self._iterate_while_data_found(output_connector, input_connector,
                                                       station, min_from_date, batch_size,
                                                       keep_looking_for_input_data, output_data_types)

            if from_date is not None and from_date.tzinfo is None:
                from_date = DEFAULT_TIMEZONE.localize(from_date)
            if from_date_across_stations is not None and from_date_across_stations.tzinfo is None:
                from_date_across_stations = DEFAULT_TIMEZONE.localize(from_date_across_stations)
            if from_date_across_stations is None or from_date < from_date_across_stations:
                from_date_across_stations = from_date

        return from_date_across_stations

    def _iterate_while_data_found(self, output_connector: ODHBaseConnector, input_connector: ODHBaseConnector,
                                  station: TrafficSensorStation, min_from_date: datetime, batch_size: int,
                                  keep_looking_for_input_data: bool,
                                  output_data_types: list[DataType] = None) -> datetime:
        from_date, keep_going = min_from_date, True
        while keep_going and from_date < get_now(from_date.tzinfo):
            from_date, keep_going = self._get_starting_date_inner(
                output_connector, input_connector, station, from_date,
                batch_size, keep_looking_for_input_data, output_data_types
            )
        return from_date

    def _get_starting_date_inner(self, output_connector: ODHBaseConnector, input_connector: ODHBaseConnector,
                                 station: TrafficSensorStation, min_from_date: datetime, batch_size: int,
                                 keep_looking_for_input_data: bool, output_data_types: list[DataType] = None
                                 ) -> Tuple[datetime | None, bool]:

        inconn_str = type(input_connector).__name__
        outconn_str = type(output_connector).__name__

        req_data_types = None
        if output_data_types:
            req_data_types = list(map(lambda x: x.name, output_data_types))
        latest_output_measure = self.__get_latest_measure(output_connector, station, data_types=req_data_types)

        filtered_input_data_types = self.get_input_data_types()
        req_data_types = None
        if filtered_input_data_types:
            req_data_types = list(map(lambda x: x.name, filtered_input_data_types))
        missing_input = input_connector and not self.__get_latest_measure(input_connector, station,
                                                                          update_create_data_types=False,
                                                                          data_types=req_data_types)
        missing_output = not latest_output_measure

        if missing_input and not keep_looking_for_input_data:
            logger.info(f"[{station.code}] No input measures on [{inconn_str}]")
            return None, False
        elif missing_output:
            logger.info(f"[{station.code}] No output measures on [{outconn_str}]")
            if self._checkpoint_cache:
                checkpoint = self._checkpoint_cache.get(
                    ComputationCheckpoint.get_id_for_station(station, self._get_manager_code()))
                if checkpoint and checkpoint.checkpoint_dt:
                    logger.info(
                        f"[{station.code}] Found checkpoint [{checkpoint.checkpoint_dt}] on [{outconn_str}], used as starting date candidate")
                    from_date = checkpoint.checkpoint_dt
                else:
                    # If there isn't any latest measure available, the min_from_date is used as starting date for the batch
                    logger.info(
                        f"[{station.code}] No checkpoint on [{outconn_str}], starting date candidate is min date "
                        f"[{min_from_date.isoformat()}]")
                    from_date = min_from_date

                if not keep_looking_for_input_data:
                    logger.info(
                        f"[{station.code}] Not keeping going, normalizing {from_date.isoformat()} "
                        f"with respect to min date "
                        f"{min_from_date.isoformat()}")
                    return self.__normalize_from_date(from_date, min_from_date, station.code)

                # if between from_date and from_date + batch_size there are no input data
                logger.info(
                    f"[{station.code}] Looking for input data on [{inconn_str}] between from_date "
                    f"{from_date.isoformat()} and from_date + batch_size ({batch_size} days)")
                to_date_tmp = from_date + timedelta(days=batch_size)
                if to_date_tmp is not None and to_date_tmp.tzinfo is None:
                    to_date_tmp = DEFAULT_TIMEZONE.localize(to_date_tmp)
                if input_connector is not None:
                    # in case, convert to env var
                    limit = 10
                    logger.info(f"Setting maximum limit to {limit} for input data request")
                    input_data = (input_connector.
                                  get_measures(from_date=from_date, to_date=to_date_tmp, station=station, limit=limit))
                    logger.info(
                        f"[{station.code}] Measures available on [{inconn_str}]: found {len(input_data)} records")
                else:
                    logger.info(f"[{station.code}] Measures available on [{inconn_str}]: no connector available")
                    input_data = []
                if len(input_data) == 0:
                    if checkpoint is None or checkpoint.checkpoint_dt is None or checkpoint.checkpoint_dt < to_date_tmp:
                        # it is pointless trying to run model, save the from_date + batch_size as checkpoint for station
                        logger.info(f"[{station.code}] Caching [{to_date_tmp}] on manager [{self._get_manager_code()}]")
                        self._checkpoint_cache.set(
                            ComputationCheckpoint(
                                station_code=station.code,
                                checkpoint_dt=to_date_tmp,
                                manager_code=self._get_manager_code()
                            )
                        )
                    # look again for more data with starting from updated checkpoint
                    logger.info(f"[{station.code}] Looking for more...")
                    return from_date, True
                else:
                    logger.info(
                        f"[{station.code}] More data in the future, normalizing {from_date.isoformat()} "
                        f"with respect to min date {min_from_date.isoformat()}")
                    return self.__normalize_from_date(from_date, min_from_date, station.code)
            else:
                # If there isn't any latest measure available, the min_from_date is used as starting date for the batch
                logger.info(
                    f"[{station.code}] No measures and no checkpoints active, using min date "
                    f"[{min_from_date.isoformat()}] as starting date")
                from_date = min_from_date
        else:
            if self._checkpoint_cache:
                checkpoint = self._checkpoint_cache.get(
                    ComputationCheckpoint.get_id_for_station(station, self._get_manager_code()))
                if checkpoint and checkpoint.checkpoint_dt and checkpoint.checkpoint_dt > latest_output_measure.valid_time:
                    logger.info(
                        f"[{station.code}] Found checkpoint date [{checkpoint.checkpoint_dt.isoformat()}] "
                        f"on [{outconn_str}], used candidate as starting date")
                    from_date = checkpoint.checkpoint_dt
                else:
                    logger.info(
                        f"[{station.code}] Measures found and no cache, using latest output measure "
                        f"[{latest_output_measure.valid_time.isoformat()}] as starting date")
                    from_date = latest_output_measure.valid_time
            else:
                logger.info(
                    f"[{station.code}] Measures found and no checkpoints active, using latest output date "
                    f"[{latest_output_measure.valid_time.isoformat()}] as starting date")
                from_date = latest_output_measure.valid_time

        logger.info(f"[{station.code}] Finally, normalize {from_date.isoformat()} "
                    f"with respect to min date {min_from_date.isoformat()}")
        return self.__normalize_from_date(from_date, min_from_date, station.code)

    def __normalize_from_date(self, from_date: datetime, min_from_date: datetime,
                              station_code: str) -> Tuple[datetime, bool]:

        if from_date.tzinfo is None:
            from_date = DEFAULT_TIMEZONE.localize(from_date)

        if min_from_date.tzinfo is None:
            min_from_date = DEFAULT_TIMEZONE.localize(min_from_date)

        if from_date.microsecond:
            from_date = from_date.replace(microsecond=0)

        if from_date < min_from_date:
            logger.warning(f"Latest measure date is [{from_date.isoformat()}] but it's before the min starting date; "
                           f"using [{min_from_date.isoformat()}] as starting date for [{station_code}]")
            from_date = min_from_date
        elif from_date > min_from_date:
            logger.info(f"[{station_code}] Using latest measure date [{from_date.isoformat()}] as starting date")

        # final date, no more iteration then False as second element of tuple returned
        return from_date, False

    def __get_latest_measure(self, connector: ODHBaseConnector,
                             station: Optional[TrafficSensorStation],
                             update_create_data_types: bool = True,
                             data_types: list[str] = None) -> Optional[Measure]:
        """
        Retrieve the latest measure for a given station. It will be the oldest one among all the measure types
        (for pollution, CO-emissions, CO2-emissions, ...) even though should be the same for all the types.

        :param station: The station for which retrieve the latest measure.
        :param data_types: The data types to filter the measures.
        :return: The latest measure for a given station.
        """
        latest_measures = connector.get_latest_measures(station, data_types=data_types)
        if latest_measures:
            if update_create_data_types:
                self._create_data_types = False
            latest_measures.sort(key=lambda x: x.valid_time)
            return latest_measures[0]

    def get_traffic_stations_from_cache(self) -> List[TrafficSensorStation]:
        """
        Returns a list of stations from cache.

        :return: List of stations from cache.
        """
        if len(self._traffic_stations) == 0:
            logger.info("Retrieving traffic station list from ODH")
            self._traffic_stations = self.__get_station_list()

        return self._traffic_stations

    def get_station_list(self) -> List[TrafficSensorStation]:
        """
        Retrieve the list of all the available stations. Override method from StationManager.
        """
        return self.get_traffic_stations_from_cache()

    def __get_station_list(self) -> List[TrafficSensorStation]:
        """
        Retrieve the list of all the available stations.
        """
        return self.station_list_connector.get_station_list()

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

    def _compute_and_upload_data(self, start_date: datetime, to_date: datetime,
                                 stations: List[TrafficSensorStation]) -> None:
        """
        Compute and upload the data for the given stations in the given interval.

        :param start_date: The starting date for the computation.
        :param to_date: The ending date for the computation.
        :param stations: The list of stations to process.
        """

        try:
            entries = self._download_data_and_compute(start_date, to_date, stations)
            self._upload_data(entries)
        except Exception as e:
            logger.exception(f"Unable to compute data from stations {_get_stations_on_logs(stations)} in the "
                             f"interval [{start_date.isoformat()}] - [{to_date.isoformat()}]", exc_info=e)

    def _update_cache(self, to_date: datetime, stations: List[TrafficSensorStation]) -> None:
        """
        Update the cache with the latest checkpoint for the given stations in the given interval.

        :param to_date: The ending date for the computation.
        :param stations: The list of stations to process.
        """

        if self._checkpoint_cache is not None:
            for station in stations:
                checkpoint = self._checkpoint_cache.get(
                    ComputationCheckpoint.get_id_for_station(station, self._get_manager_code()))
                if checkpoint and checkpoint.checkpoint_dt:
                    logger.info(f"[{station.code}] Cache found on manager [{self._get_manager_code()}]: "
                                f"[{checkpoint.checkpoint_dt}]; comparing with {to_date.isoformat()}")
                latest_date = self._get_latest_date(connector=self.get_input_connector(), stations=[station])
                if checkpoint is None or checkpoint.checkpoint_dt is None \
                        or (checkpoint.checkpoint_dt < to_date and checkpoint.checkpoint_dt < latest_date):
                    logger.info(
                        f"[{station.code}] Caching [{to_date.isoformat()}] on manager [{self._get_manager_code()}]")
                    self._checkpoint_cache.set(
                        ComputationCheckpoint(
                            station_code=station.code,
                            checkpoint_dt=to_date,
                            manager_code=self._get_manager_code()
                        )
                    )
                else:
                    if checkpoint and checkpoint.checkpoint_dt and checkpoint.checkpoint_dt > latest_date:
                        logger.info(f"[{station.code}] Cache available but cache writing skipped as latest date is prior to checkpoint.")
                    else:
                        logger.info(f"[{station.code}] Cache available but cache writing skipped.")
        else:
            logger.info(f"Cache unavailable, unable to cache date.")

    def run_computation(self,
                        stations: List[TrafficSensorStation],
                        min_from_date: datetime,
                        max_to_date: datetime,
                        batch_size: int,
                        keep_looking_for_input_data: bool,
                        use_hours_for_batch_size: bool = False) -> None:  # TODO: check if this is still needed
        """
        Start the computation of a batch of data measures on a specific station.
        As starting date for the  batch is used the latest measure available on the ODH,
        if no measures are available min_from_date is used.

        :param stations: List of stations to process.
        :param min_from_date: Traffic measures before this date are discarded if no measures are available.
        :param max_to_date: Ending date for interval; measures after this date are discarded.
        :param batch_size: Number of days or hours to be processed as maximum span.
        :param keep_looking_for_input_data: If input data has no data, updates checkpoint and goes on looking for data:
                                            Useful to find the first traffic data for a station on validation
                                            To be avoided when there are no validation data on pollution (wait for them)
        :param use_hours_for_batch_size: If True, the batch size is considered in hours instead of days.
        """

        logger.info(f"Determining computation interval for {_get_stations_on_logs(stations)} "
                    f"between [{min_from_date.isoformat()}] and [{max_to_date.isoformat()}]")

        logger.info(f"Looking for latest measures available on [{type(self.get_output_connector()).__name__}] ")
        start_date = self.get_starting_date(self.get_output_connector(), self.get_input_connector(),
                                            stations, min_from_date, batch_size, keep_looking_for_input_data)

        if start_date is None or start_date == max_to_date:
            logger.info(f"Not computing data for stations {_get_stations_on_logs(stations)} in interval "
                        f"[{start_date.isoformat() if start_date else 'no-date'} - "
                        f"no-date] (no timespan)")
        elif start_date < max_to_date:
            # Detect inactive stations:
            # If we're about to request more than one window of measurements, do a check first if there even is any new data
            batch_diff = (max_to_date - start_date).days if not use_hours_for_batch_size \
                else (max_to_date - start_date).seconds // 3600
            if start_date is not None and batch_diff > batch_size:
                latest_measurement_date = self._get_latest_date(self.get_input_connector(), stations)
                # traffic data request range end is the latest measurement
                # For inactive stations, this latest measurement date will be < start_date,
                # thus no further requests will be made. In general, it makes no sense to ask for data
                # beyond the latest measurement, if we already know which date that is.
                if latest_measurement_date < max_to_date:
                    logger.info(
                        f"Using latest input measurement date {latest_measurement_date.isoformat()} "
                        f"as maximum end date for data request")
                max_to_date = min(max_to_date, latest_measurement_date)

            to_date = start_date

            if use_hours_for_batch_size:
                to_date = to_date + timedelta(hours=batch_size)
            else:
                to_date = to_date + timedelta(days=batch_size)
            if to_date > max_to_date:
                to_date = max_to_date

            if to_date is not None and to_date.tzinfo is None:
                to_date = DEFAULT_TIMEZONE.localize(to_date)

            logger.info(f"Computing data for stations {_get_stations_on_logs(stations)} in interval "
                        f"[{start_date.isoformat()} - {to_date.isoformat()}]")

            self._compute_and_upload_data(start_date, to_date, stations)

            self._update_cache(to_date, stations)
        else:
            logger.info(f"Nothing to process for stations {_get_stations_on_logs(stations)} in interval "
                        f"[{start_date.isoformat()} - no-date]")

    def run_computation_and_upload_results(self,
                                           min_from_date: datetime,
                                           max_to_date: datetime,
                                           batch_size: int,
                                           run_on_all_stations: bool) -> None:
        """
        Watch-out! Used only from main_*!

        Start the computation of a batch of data measures. As starting date for the batch is used the latest
        measure available on the ODH, if no measures are available min_from_date is used.

        :param min_from_date: Traffic measures before this date are discarded if no measures are available.
        :param max_to_date: Traffic measure after this date are discarded.
        :param batch_size: Number of days to be processed as maximum span.
        :param run_on_all_stations: Defines if the run must be done on all stations at the same time
        """

        if min_from_date.tzinfo is None:
            min_from_date = DEFAULT_TIMEZONE.localize(min_from_date)

        if max_to_date.tzinfo is None:
            max_to_date = DEFAULT_TIMEZONE.localize(max_to_date)

        computation_start_dt = get_now()

        stations = self.get_traffic_stations_from_cache()

        stations_no_famas_traffic = [station for station in stations if station.origin != 'FAMAS-traffic']
        logger.info(f"Stations filtered excluding 'FAMAS-traffic', resulting {len(stations_no_famas_traffic)} "
                    f"elements (starting from {len(stations)})")
        stations_with_km = [station for station in stations_no_famas_traffic if station.km > 0]
        logger.info(f"Stations filtered on having km defined, resulting {len(stations_with_km)} "
                    f"elements (starting from {len(stations_no_famas_traffic)})")
        stations_with_km_indloop = [station for station in stations_with_km
                                    if station.sensor_type is not None and station.sensor_type == 'induction_loop']
        logger.info(f"Stations filtered on sensor_type being induction_loop, resulting {len(stations_with_km_indloop)} "
                    f"elements (starting from {len(stations_with_km)})")

        if run_on_all_stations:
            self._run_computation_on_all_stations(stations_with_km_indloop, min_from_date, max_to_date, batch_size)
        else:
            self._run_computation_on_single_station(stations_with_km_indloop, min_from_date, max_to_date, batch_size)

        computation_end_dt = get_now()
        logger.info(f"Completed computation in [{(computation_end_dt - computation_start_dt).seconds}]")

    def _run_computation_on_single_station(self, stations, min_from_date, max_to_date, batch_size):
        for station in stations:
            self.run_computation([station], min_from_date, max_to_date, batch_size, False)

    def _run_computation_on_all_stations(self, stations, min_from_date, max_to_date, batch_size):
        self.run_computation(stations, min_from_date, max_to_date, batch_size, True)
