# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

import yaml

from common.cache.computation_checkpoint import ComputationCheckpointCache
from common.connector.collector import ConnectorCollector
from common.data_model import TrafficSensorStation, Station, RoadWeatherObservationMeasureCollection, Provenance
from common.data_model.entry import GenericEntry
from common.manager.station import StationManager
from common.settings import ROAD_WEATHER_CONFIG_FILE, TMP_DIR
from road_weather.manager._forecast import Forecast
from road_weather.model.road_weather_model import RoadWeatherModel

logger = logging.getLogger("pollution_v2.road_weather.manager.road_weather")


class RoadWeatherManager(StationManager):
    """
    Manager in charge of executing pollution computation.
    """

    def __init__(self, connector_collector: ConnectorCollector, provenance: Provenance,
                 checkpoint_cache: Optional[ComputationCheckpointCache] = None) -> None:
        super().__init__(connector_collector, provenance, checkpoint_cache)
        self.station_list_connector = connector_collector.road_weather_observation

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

        connector = self._connector_collector.road_weather_observation
        logger.info(f"Downloading observation data for station [{traffic_station.code}] from [{from_date}] to [{to_date}]")
        return RoadWeatherObservationMeasureCollection(
            measures=connector.get_measures(from_date=from_date, to_date=to_date, station=traffic_station)
        )

    def _download_forecast_data(self, traffic_station: Station) -> Tuple[str, str]: # TODO: change with RoadWeatherForecastMeasureCollection
        """
        Download forecast data measures in the given interval.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting RoadWeatherObservationMeasureCollection containing the road weather forecast data.
        """

        # !!!: temporarily downloading forecast data of WRF from CISMA
        # TODO: replace with the actual forecast data from ODH when available

        station_code = traffic_station.code

        with open(ROAD_WEATHER_CONFIG_FILE, 'r') as file:
            config = yaml.safe_load(file)
            # ODH station code -> WRF station code
            station_mapping = config['mappings']

        station_mapping = {str(k): str(v) for k, v in station_mapping.items()}
        if str(station_code) not in station_mapping:
            logger.error(f"Station code [{station_code}] not found in the mapping [{ROAD_WEATHER_CONFIG_FILE}]")
            raise ValueError(f"Station code [{station_code}] not found in the mapping")

        logger.info("Found mapping for ODH station code [" + str(str(station_code)) + "] -> "
                    "CISMA station code [" + str(station_mapping[station_code]) + "]")
        logger.info(f"Downloading forecast data for station [{station_code}] from CISMA")
        wrf_station_code = station_mapping[str(station_code)]
        xml_url = f"https://www.cisma.bz.it/wrf-alpha/CR/1{wrf_station_code}.xml"

        forecast = Forecast(wrf_station_code)
        forecast.download_xml(xml_url)
        forecast.interpolate_hourly()
        forecast.negative_radiation_filter()
        roadcast_start = forecast.start
        logger.info('forecast - XML processed correctly')
        forecast_filename = f"{TMP_DIR}/forecast_{wrf_station_code}_{roadcast_start}.xml"
        forecast.to_xml(forecast_filename)
        logger.info(f'forecast - XML saved in {forecast_filename} ')
        return forecast_filename, roadcast_start

    def _compute_observation_start_end_dates(self, forecast_start: str) -> Tuple[datetime, datetime]:
        """
        Compute the start and end dates for the observation computation.

        :param forecast_start: The forecast start date string.
        :return: The start and end dates for the observation computation.
        """

        # start_obs = forecast.start - 12 h
        # end_obs = forecast.start + 8 h
        forecast_start = datetime.strptime(forecast_start, '%Y-%m-%dT%H:%M')
        start_date = forecast_start - timedelta(hours=12)
        end_date = forecast_start + timedelta(hours=8)
        return start_date, end_date

    def _download_data_and_compute(self, station: Station) -> List[GenericEntry]:

        if not station:
            logger.error(f"Cannot compute road condition on empty station")
            return []

        observation_data = []
        forecast_data_xml_path = ""
        forecast_start = ""
        try:
            # TODO: change with actual implementation from ODH when available
            forecast_data_xml_path, forecast_start = self._download_forecast_data(station)

            start_date, to_date = self._compute_observation_start_end_dates(forecast_start)

            observation_data = self._download_observation_data(start_date, to_date, station)
        except Exception as e:
            logger.exception(
                f"Unable to download observation and forecast data for station [{station.code}]",
                exc_info=e)

        if observation_data and forecast_data_xml_path:
            model = RoadWeatherModel()
            return model.compute_data(observation_data, forecast_data_xml_path, forecast_start, station)

        return []

    def run_computation_for_single_station(self, station: Station) -> None:
        """
        Run the computation for a single station.

        :param station: The station for which to run the computation.
        """
        self._download_data_and_compute(station)
