# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

from common.cache.computation_checkpoint import ComputationCheckpointCache
from common.connector.collector import ConnectorCollector
from common.connector.common import ODHBaseConnector
from common.data_model import Station, RoadWeatherObservationMeasureCollection, Provenance, DataType, MeasureCollection
from common.data_model.entry import GenericEntry
from common.data_model.roadcast import RoadCastMeasure, RoadCastEntry, RoadCastMeasureCollection, RoadCastClass, \
    RoadCastTypeClass, ExtendedRoadCastEntry
from common.manager.station import StationManager
from common.settings import TMP_DIR, DEFAULT_TIMEZONE
from road_weather.manager._forecast import Forecast
from road_weather.model.road_weather_model import RoadWeatherModel

logger = logging.getLogger("pollution_v2.pollution_dispersal.manager.pollution_dispersal")


class PollutionDispersalManager(StationManager):
    """
    Manager in charge of executing pollution computation.
    """

    def __init__(self, connector_collector: ConnectorCollector, provenance: Provenance,
                 checkpoint_cache: Optional[ComputationCheckpointCache] = None) -> None:
        super().__init__(connector_collector, provenance, checkpoint_cache)
        # TODO a che serve?
        self.station_list_connector = self.get_input_connector()

    def get_input_connector(self) -> ODHBaseConnector:
        return self._connector_collector.pollution

    def get_output_connector(self) -> ODHBaseConnector:
        return self._connector_collector.road_weather_forecast

    def get_output_additional_connector(self) -> ODHBaseConnector:
        return self._connector_collector.road_weather_conf_level

    def _get_data_types(self) -> List[DataType]:
        return RoadCastMeasure.get_data_types()

    def _build_from_entries(self, input_entries: List[RoadCastEntry]) -> MeasureCollection:
        return RoadCastMeasureCollection.build_from_entries(input_entries, self._provenance)

    def _download_observation_data(self,
                                   from_date: datetime,
                                   to_date: datetime,
                                   traffic_station: Station
                                   ) -> RoadWeatherObservationMeasureCollection:
        """
        Download observation data measures in the given interval.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting RoadWeatherObservationMeasureCollection containing the road weather observation data.
        """

        connector = self.get_input_connector()
        logger.info(f"Downloading observation data for station [{traffic_station.code}] from [{from_date}] to [{to_date}]")
        return RoadWeatherObservationMeasureCollection(
            measures=connector.get_measures(from_date=from_date, to_date=to_date, station=traffic_station)
        )

    def _download_forecast_data(self, traffic_station: Station) -> Tuple[str, datetime]: # TODO: change with RoadWeatherForecastMeasureCollection
        """
        Download forecast data measures in the given interval.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting RoadWeatherObservationMeasureCollection containing the road weather forecast data.
        """

        # !!!: temporarily downloading forecast data of WRF from CISMA
        # TODO: replace with the actual forecast data from ODH when available

        xml_url = f"https://www.cisma.bz.it/wrf-alpha/CR/{traffic_station.wrf_code}.xml"

        forecast = Forecast(traffic_station.wrf_code)
        forecast.download_xml(xml_url)
        forecast.interpolate_hourly()
        forecast.negative_radiation_filter()
        roadcast_start = forecast.start
        logger.info('forecast - XML processed correctly')
        forecast_filename = f"{TMP_DIR}/forecast_{traffic_station.wrf_code}_{roadcast_start}.xml"
        forecast.to_xml(forecast_filename)
        logger.info(f'forecast - XML saved in {forecast_filename} ')

        roadcast_start = datetime.strptime(roadcast_start, '%Y-%m-%dT%H:%M')
        if roadcast_start.tzinfo is None:
            roadcast_start = DEFAULT_TIMEZONE.localize(roadcast_start)

        return forecast_filename, roadcast_start

    def _compute_observation_start_end_dates(self, forecast_start: datetime) -> Tuple[datetime, datetime]:
        """
        Compute the start and end dates for the observation computation.

        :param forecast_start: The forecast start date string.
        :return: The start and end dates for the observation computation.
        """

        # start_obs = forecast.start - 16 h
        start_date = forecast_start - timedelta(hours=16)
        if start_date.tzinfo is None:
            start_date = DEFAULT_TIMEZONE.localize(start_date)

        # end_obs = forecast.start + 8 h
        end_date = forecast_start + timedelta(hours=8)
        if end_date.tzinfo is None:
            end_date = DEFAULT_TIMEZONE.localize(end_date)

        return start_date, end_date

    def _download_data_and_compute(self, station: Station) -> List[GenericEntry]:

        if not station:
            logger.error(f"Cannot compute road condition on empty station")
            return []

        observation_data = []
        to_date = None
        forecast_data_xml_path = ""
        forecast_start = None
        max_observation_data = None
        try:
            # TODO: change with actual implementation from ODH when available
            forecast_data_xml_path, forecast_start = self._download_forecast_data(station)

            start_date, to_date = self._compute_observation_start_end_dates(forecast_start)

            observation_data = self._download_observation_data(start_date, to_date, station)
            max_observation_data = max([item.valid_time for item in observation_data.get_entries()])
        except Exception as e:
            logger.exception(
                f"Unable to download observation and forecast data for station [{station.code}]",
                exc_info=e)

        if max_observation_data and observation_data and forecast_data_xml_path:
            model = RoadWeatherModel()
            res: list[ExtendedRoadCastEntry] = model.compute_data(observation_data, forecast_data_xml_path,
                                                                  forecast_start, station)
            logger.info(f"Received {len(res)} records from road weahter WS")
            res = [item for item in res if item.valid_time > max_observation_data]
            logger.info(f"Remaining with {len(res)} records from road weahter WS once filter on date {max_observation_data} is applied")
            return res

        return []

    def run_computation_for_single_station(self, station: Station) -> None:
        """
        Run the computation for a single station.

        :param station: The station for which to run the computation.
        """
        entries = self._download_data_and_compute(station)
        self._upload_data(entries)

        # reading entries, extracts the confidence level and creates a dedicated entry
        if (len(entries) > 0 and
                hasattr(self, "get_output_additional_connector") and self.get_output_additional_connector()):
            reference_entry = entries[0]
            entry = RoadCastEntry(
                station=reference_entry.station,
                valid_time=reference_entry.valid_time,
                roadcast_class=RoadCastClass.ROADCAST,
                entry_class=RoadCastTypeClass.RW_FORECAST_CONF_LEVEL,
                entry_value=reference_entry.conf_level,
                period=1
            )
            self._upload_data([entry], self.get_output_additional_connector())

