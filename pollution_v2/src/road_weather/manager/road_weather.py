# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import os
import logging
from datetime import datetime, timedelta
from typing import List, Tuple

from common.cache.common import TrafficManagerClass
from common.connector.common import ODHBaseConnector
from common.data_model import TrafficSensorStation, TrafficMeasureCollection, Station
from common.data_model.entry import GenericEntry
from common.data_model.road_weather import RoadWeatherObservationMeasureCollection, RoadWeatherForecastMeasureCollection
from common.data_model.validation import ValidationMeasureCollection
from common.manager.traffic_station import TrafficStationManager
from common.data_model.common import DataType, MeasureCollection
from common.data_model.pollution import PollutionMeasure, PollutionMeasureCollection, PollutionEntry
from pollution_connector.model.pollution_computation_model import PollutionComputationModel
from road_weather.manager._forecast import Forecast
from road_weather.model.road_weather_model import RoadWeatherModel

logger = logging.getLogger("pollution_v2.road_weather.manager.road_weather")


class RoadWeatherManager(TrafficStationManager):
    """
    Manager in charge of executing pollution computation.
    """

    # def _get_manager_code(self) -> str:
    #     return "ROADWEATHER"
    #
    # def get_output_connector(self) -> ODHBaseConnector:
    #     return self._connector_collector.pollution
    #
    # def get_input_connector(self) -> ODHBaseConnector:
    #     # on v1 it would have been self._connector_collector.traffic
    #     return self._connector_collector.validation

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
        # TODO: replace with the actual forecast data when available

        station_code = traffic_station.code
        xml_url = f"https://www.cisma.bz.it/wrf-alpha/CR/{station_code}.xml"

        forecast = Forecast(station_code)
        forecast.download_xml(xml_url)
        forecast.interpolate_hourly()
        forecast.negative_radiation_filter()
        roadcast_start = forecast.start
        print('* forecast - XML processed correctly')
        project_root = os.path.abspath(os.path.dirname(__name__))
        forecast_filename = f"{project_root}/data/forecast/forecast_{station_code}_{roadcast_start}.xml"
        forecast.to_xml(forecast_filename)
        print('* forecast - XML saved')
        return forecast_filename, roadcast_start

    def _compute_start_end_dates(self, forecast_start: str) -> Tuple[datetime, datetime]:
        """
        Compute the start and end dates for the computation.

        :param forecast_start: The forecast start date string.
        :return: The start and end dates for the computation.
        """

        # start_obs = forecast.start - 12 h
        # end_obs = forecast.start + 8 h
        forecast_start = datetime.strptime(forecast_start, '%Y-%m-%dT%H:%M')
        start_date = forecast_start - timedelta(hours=12)
        end_date = forecast_start + timedelta(hours=8)
        return start_date, end_date


    def _download_data_and_compute_for_single_station(self, station: TrafficSensorStation) -> List[GenericEntry]:

        if not station:
            logger.error(f"Cannot compute road condition on empty station")
            return []

        observation_data = []
        forecast_data_xml_path = ""
        forecast_start = ""
        try:
            # TODO: change with actual implementation when available
            forecast_data_xml_path, forecast_start = self._download_forecast_data(station)

            start_date, to_date = self._compute_start_end_dates(forecast_start)

            observation_data = self._download_observation_data(start_date, to_date, station)
        except Exception as e:
            logger.exception(
                f"Unable to download observation and forecast data for station [{station.code}]",
                exc_info=e)

        if observation_data and forecast_data_xml_path:
            model = RoadWeatherModel()
            return model.compute_data(observation_data, forecast_data_xml_path, forecast_start, station)

        return []

    def run_computation_for_single_station(self, station: TrafficSensorStation) -> None:
        """
        Run the computation for a single station.

        :param station: The station for which to run the computation.
        """
        self._download_data_and_compute_for_single_station(station)


    # def _get_data_types(self) -> List[DataType]:
    #     return PollutionMeasure.get_data_types()
    #
    # def _build_from_entries(self, input_entries: List[PollutionEntry]) -> MeasureCollection:
    #     return PollutionMeasureCollection.build_from_entries(input_entries, self._provenance)
