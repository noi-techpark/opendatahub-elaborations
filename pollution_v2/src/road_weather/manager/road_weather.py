# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from datetime import datetime
from typing import List

from common.cache.common import TrafficManagerClass
from common.connector.common import ODHBaseConnector
from common.data_model import TrafficSensorStation, TrafficMeasureCollection
from common.data_model.entry import GenericEntry
from common.data_model.road_weather import RoadWeatherObservationMeasureCollection
from common.data_model.validation import ValidationMeasureCollection
from common.manager.traffic_station import TrafficStationManager
from common.data_model.common import DataType, MeasureCollection
from common.data_model.pollution import PollutionMeasure, PollutionMeasureCollection, PollutionEntry
from pollution_connector.model.pollution_computation_model import PollutionComputationModel

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
                                   traffic_station: TrafficSensorStation
                                   ) -> RoadWeatherObservationMeasureCollection:
        """
        Download observation data measures in the given interval.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting RoadWeatherObservationMeasureCollection containing the road weather observation data.
        """

        return RoadWeatherObservationMeasureCollection(
            measures=self._connector_collector.road_weather.get_measures(from_date=from_date, to_date=to_date,
                                                                         station=traffic_station))

    def _download_forecast_data(self,
                                from_date: datetime,
                                to_date: datetime,
                                traffic_station: TrafficSensorStation
                                ) -> RoadWeatherObservationMeasureCollection: # TODO: change
        """
        Download forecast data measures in the given interval.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting RoadWeatherObservationMeasureCollection containing the road weather forecast data.
        """

        # !!!: temporarily downloading forecast data of WRF from CISMA
        # TODO: replace with the actual forecast data when available

        # implement retrieval of forecast data from CISMA

    def _download_data_and_compute(self, start_date: datetime, to_date: datetime,
                                   stations: List[TrafficSensorStation]) -> List[GenericEntry]:

        if len(stations) != 1:
            logger.error(f"Cannot compute road condition on more than one station ({len(stations)} passed)")
            return []

        traffic_station = stations[0]

        observation_data = []
        forecast_data = []
        try:
            observation_data = self._download_observation_data(start_date, to_date, traffic_station)
            forecast_data = self._download_forecast_data(start_date, to_date, traffic_station)
        except Exception as e:
            logger.exception(
                f"Unable to download observation and forecast data for station [{traffic_station.code}] "
                f"in the interval [{start_date.isoformat()}] - [{to_date.isoformat()}]",
                exc_info=e)

        # if observation_data and traffic_data:
        #     model = PollutionComputationModel()
        #     return model.compute_data(observation_data, TrafficMeasureCollection(traffic_data), traffic_station)

        return []


    # def _get_data_types(self) -> List[DataType]:
    #     return PollutionMeasure.get_data_types()
    #
    # def _build_from_entries(self, input_entries: List[PollutionEntry]) -> MeasureCollection:
    #     return PollutionMeasureCollection.build_from_entries(input_entries, self._provenance)
