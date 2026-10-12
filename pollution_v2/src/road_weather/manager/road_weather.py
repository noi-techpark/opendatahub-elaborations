# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional

from common.cache.common import TrafficManagerClass
from common.cache.computation_checkpoint import ComputationCheckpointCache, ComputationCheckpoint
from common.connector.collector import ConnectorCollector
from common.connector.common import ODHBaseConnector
from common.data_model import Station, RoadWeatherObservationMeasureCollection, Provenance, DataType, MeasureCollection
from common.data_model.roadcast import RoadCastMeasure, RoadCastEntry, RoadCastMeasureCollection, RoadCastClass, \
    RoadCastTypeClass, ExtendedRoadCastEntry
from common.manager.station import StationManager
from common.settings import TMP_DIR, PERIOD_1SEC
from road_weather.manager._forecast import Forecast
from road_weather.model.road_weather_model import RoadWeatherModel

logger = logging.getLogger("pollution_v2.road_weather.manager.road_weather")

# CISMA WRF forecasts for the road weather stations; {} is the station WRF code
FORECAST_URL_TEMPLATE = "https://www.cisma.bz.it/wrf-alpha/CR/{}.xml"


class RoadWeatherManager(StationManager):
    """
    Manager in charge of computing the road condition forecast of the road weather (RWIS) stations.

    Differently from the traffic managers, it does not walk through batches of past data: each run takes the latest
    available WRF forecast, together with the observations around its start, and computes the roadcast. The
    checkpoint cache stores the start of the last forecast successfully processed for each station, so that a forecast
    is not computed twice.
    """

    def __init__(self, connector_collector: ConnectorCollector, provenance: Provenance,
                 checkpoint_cache: Optional[ComputationCheckpointCache] = None) -> None:
        super().__init__(connector_collector, provenance, checkpoint_cache)
        self.station_list_connector = self.get_input_connector()

    def get_input_connector(self) -> ODHBaseConnector:
        return self._connector_collector.road_weather_observation

    def get_output_connector(self) -> ODHBaseConnector:
        return self._connector_collector.road_weather_forecast

    def get_output_additional_connector(self) -> ODHBaseConnector:
        return self._connector_collector.road_weather_conf_level

    def _get_manager_code(self) -> str:
        return TrafficManagerClass.ROAD_WEATHER.name

    def _get_data_types(self) -> List[DataType]:
        return RoadCastMeasure.get_data_types()

    def _build_from_entries(self, input_entries: List[RoadCastEntry]) -> MeasureCollection:
        return RoadCastMeasureCollection.build_from_entries(input_entries, self._provenance)

    def _download_observation_data(self,
                                   from_date: datetime,
                                   to_date: datetime,
                                   station: Station
                                   ) -> RoadWeatherObservationMeasureCollection:
        """
        Download observation data measures in the given interval.

        :param from_date: Measures before this date are discarded.
        :param to_date: Measures after this date are discarded.
        :return: The resulting RoadWeatherObservationMeasureCollection containing the road weather observation data.
        """

        connector = self.get_input_connector()
        logger.info(f"Downloading observation data for station [{station.code}] from [{from_date.isoformat()}] "
                    f"to [{to_date.isoformat()}]")
        return RoadWeatherObservationMeasureCollection(
            measures=connector.get_measures(from_date=from_date, to_date=to_date, station=station)
        )

    def _download_forecast_data(self, station: Station) -> Tuple[str, datetime]:  # TODO: change with RoadWeatherForecastMeasureCollection
        """
        Download the latest forecast of the station, interpolate it hourly and save it in a temporary file.

        :return: The name of the forecast file, to be removed by the caller, and the start of the forecast (UTC).
        """

        # !!!: temporarily downloading forecast data of WRF from CISMA
        # TODO: replace with the actual forecast data from ODH when available

        forecast = Forecast(station.wrf_code)
        forecast.download_xml(FORECAST_URL_TEMPLATE.format(station.wrf_code))
        forecast.interpolate_hourly()
        forecast.negative_radiation_filter()
        logger.info('forecast - XML processed correctly')

        forecast_filename = f"{TMP_DIR}/forecast_{station.wrf_code}_{forecast.start}.xml"
        forecast.to_xml(forecast_filename)
        logger.info(f'forecast - XML saved in {forecast_filename}')

        # the forecast times are in UTC (see the "Z" suffix of forecast-time)
        forecast_start = datetime.strptime(forecast.start, '%Y-%m-%dT%H:%M').replace(tzinfo=timezone.utc)
        return forecast_filename, forecast_start

    @staticmethod
    def _compute_observation_start_end_dates(forecast_start: datetime) -> Tuple[datetime, datetime]:
        """
        Compute the start and end dates for the observations to be used with the forecast.

        :param forecast_start: The (timezone aware) forecast start.
        :return: The start (forecast start - 16 h) and end (forecast start + 8 h) dates.
        """
        return forecast_start - timedelta(hours=16), forecast_start + timedelta(hours=8)

    def _get_checkpoint(self, station: Station) -> Optional[datetime]:
        if not self._checkpoint_cache:
            return None
        checkpoint = self._checkpoint_cache.get(
            ComputationCheckpoint.get_id_for_station(station, self._get_manager_code()))
        return checkpoint.checkpoint_dt if checkpoint else None

    def _set_checkpoint(self, station: Station, forecast_start: datetime) -> None:
        if self._checkpoint_cache:
            self._checkpoint_cache.set(ComputationCheckpoint(
                station_code=station.code,
                checkpoint_dt=forecast_start,
                manager_code=self._get_manager_code()
            ))

    def _download_data_and_compute(self, station: Station, forecast_filename: str,
                                   forecast_start: datetime) -> List[ExtendedRoadCastEntry]:
        """
        Download the observations around the forecast start and compute the road condition forecast, keeping only the
        entries after the latest observation (ODH does not accept data older than the latest available).
        """

        start_date, to_date = self._compute_observation_start_end_dates(forecast_start)
        observation_data = self._download_observation_data(start_date, to_date, station)
        observation_times = [item.valid_time for item in observation_data.get_entries()]
        if not observation_times:
            logger.warning(f"No observations available for station [{station.code}], unable to compute road condition")
            return []
        max_observation_time = max(observation_times)

        try:
            res = RoadWeatherModel().compute_data(observation_data, forecast_filename, forecast_start, station)
        except ValueError as e:
            # METRo requires some valid observations, which may become available later
            logger.warning(f"Observations of station [{station.code}] not suitable for METRo, skipping: {e}")
            return []
        logger.info(f"Received {len(res)} records from road weather WS")
        res = [item for item in res if item.valid_time > max_observation_time]
        logger.info(f"Remaining with {len(res)} records from road weather WS once filter on date "
                    f"{max_observation_time} is applied")
        return res

    def run_computation_for_single_station(self, station: Station) -> int:
        """
        Run the computation for a single station, if a forecast more recent than the last processed one is available.

        :param station: The station, with `wrf_code` set.
        :return: The number of entries uploaded.
        """
        if not station or not station.wrf_code:
            logger.error(f"Cannot compute road condition on a station without WRF code: [{station}]")
            return 0

        forecast_filename, forecast_start = self._download_forecast_data(station)
        try:
            last_processed = self._get_checkpoint(station)
            if last_processed is not None and last_processed >= forecast_start:
                logger.info(f"[{station.code}] Forecast starting at [{forecast_start.isoformat()}] already processed "
                            f"(checkpoint [{last_processed.isoformat()}]), skipping")
                return 0

            entries = self._download_data_and_compute(station, forecast_filename, forecast_start)
            if not entries:
                return 0
            self._upload_data(entries)

            # reading entries, extracts the confidence level and creates a dedicated entry
            reference_entry = entries[0]
            if reference_entry.conf_level is not None:
                entry = RoadCastEntry(
                    station=reference_entry.station,
                    valid_time=reference_entry.valid_time,
                    roadcast_class=RoadCastClass.ROADCAST,
                    entry_class=RoadCastTypeClass.RW_FORECAST_CONF_LEVEL,
                    entry_value=reference_entry.conf_level,
                    period=PERIOD_1SEC
                )
                self._upload_data([entry], self.get_output_additional_connector())

            self._set_checkpoint(station, forecast_start)
            return len(entries)
        finally:
            if os.path.exists(forecast_filename):
                os.remove(forecast_filename)
