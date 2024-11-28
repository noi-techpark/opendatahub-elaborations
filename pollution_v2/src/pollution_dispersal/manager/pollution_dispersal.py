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
from common.data_model import Station, RoadWeatherObservationMeasureCollection, Provenance, DataType, MeasureCollection, \
    PollutionDispersalMeasureCollection, PollutionMeasureCollection, PollutionDispersalMeasure
from common.data_model.entry import GenericEntry
from common.data_model.roadcast import RoadCastMeasure, RoadCastEntry, RoadCastMeasureCollection, RoadCastClass, \
    RoadCastTypeClass, ExtendedRoadCastEntry
from common.data_model.weather import WeatherMeasureCollection
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
        self.station_list_connector = self.get_input_connector()

    def get_input_connector(self) -> ODHBaseConnector:
        return self._connector_collector.pollution

    def get_input_additional_connector(self) -> ODHBaseConnector:
        return self._connector_collector.weather

    def get_output_connector(self) -> ODHBaseConnector:
        return self._connector_collector.road_weather_forecast

    def _get_data_types(self) -> List[DataType]:
        return PollutionDispersalMeasure.get_data_types()

    def _build_from_entries(self, input_entries: List[RoadCastEntry]) -> MeasureCollection:
        pass
        # return PollutionDispersalMeasureCollection.build_from_entries(input_entries, self._provenance)

    def _download_pollution_data(self,
                                   from_date: datetime,
                                   to_date: datetime,
                                   traffic_station: Station
                                   ) -> PollutionMeasureCollection:
        """
        Download pollution data measures in the given interval.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting PollutionMeasureCollection containing the pollution data.
        """

        connector = self.get_input_connector()
        logger.info(f"Downloading pollution data for station [{traffic_station.code}] from [{from_date}] to [{to_date}]")
        return PollutionMeasureCollection(
            measures=connector.get_measures(from_date=from_date, to_date=to_date, station=traffic_station)
        )

    def _download_weather_data(self,
                                   from_date: datetime,
                                   to_date: datetime,
                                   station: Station
                                   ) -> WeatherMeasureCollection:
        """
        Download weather data measures in the given interval.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting WeatherMeasureCollection containing the weather data.
        """

        temp_station_code = station.code
        station.code = station.meteo_station_code

        connector = self.get_input_additional_connector()
        logger.info(f"Downloading weather data for meteo station [{station.code}] from [{from_date}] to [{to_date}]")
        collection = WeatherMeasureCollection(
            measures=connector.get_measures(from_date=from_date, to_date=to_date, station=station)
        )

        station.code = temp_station_code
        return collection

    def _download_data_and_compute(self, station: Station, from_date: datetime, to_date: datetime) -> List[GenericEntry]:

        if not station:
            logger.error(f"Cannot compute pollution dispersal on empty station")
            return []

        pollution_data = []
        weather_data = []
        try:
            pollution_data = self._download_pollution_data(from_date, to_date, station)
            weather_data = self._download_weather_data(from_date, to_date, station)
        except Exception as e:
            logger.exception(
                f"Unable to download pollution and weather data for station [{station.code}]",
                exc_info=e)

        if pollution_data and weather_data:
            print("pollution_data", pollution_data)
            print("weather_data", weather_data)
            # model = RoadWeatherModel()
            # res: list[ExtendedRoadCastEntry] = model.compute_data(observation_data, forecast_data_xml_path,
            #                                                       forecast_start, station)
            # logger.info(f"Received {len(res)} records from road weahter WS")
            # res = [item for item in res if item.valid_time > max_observation_data]
            # logger.info(f"Remaining with {len(res)} records from road weahter WS once filter on date {max_observation_data} is applied")
            # return res

        return []

    def run_computation_for_single_station(self, station: Station, from_date: datetime, to_date: datetime) -> None:
        """
        Run the computation for a single station.
        Retrieves data in the given interval, computes the pollution dispersal and uploads the results.

        :param station: The station for which to run the computation.
        """
        entries = self._download_data_and_compute(station, from_date, to_date)
        # self._upload_data(entries)
