# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from common.cache.common import TrafficManagerClass
from common.cache.computation_checkpoint import ComputationCheckpointCache
from common.connector.collector import ConnectorCollector
from common.connector.common import ODHBaseConnector
from common.data_model import Provenance, DataType, MeasureCollection, PollutionMeasureCollection, \
    PollutionDispersalMeasure, TrafficSensorStation, PollutionMeasure, PollutantClass, Station
from common.data_model.entry import GenericEntry
from common.data_model.pollution_dispersal import PollutionDispersalEntry, PollutionDispersalMeasureCollection
from common.data_model.weather import WeatherMeasureCollection
from common.manager.station import StationManager
from common.settings import DAG_POLLUTION_DISPERSAL_TRIGGER_DAG_HOURS_SPAN
from pollution_dispersal.model.pollution_dispersal_model import PollutionDispersalModel

logger = logging.getLogger("pollution_v2.pollution_dispersal.manager.pollution_dispersal")


class PollutionDispersalManager(StationManager):
    """
    Manager in charge of executing pollution computation.
    """

    def __init__(self, connector_collector: ConnectorCollector, provenance: Provenance,
                 checkpoint_cache: Optional[ComputationCheckpointCache] = None) -> None:
        super().__init__(connector_collector, provenance, checkpoint_cache)
        self.station_list_connector = self.get_input_connector()

    def _get_manager_code(self) -> str:
        return TrafficManagerClass.DISPERSAL.name

    def get_input_connector(self) -> ODHBaseConnector:
        return self._connector_collector.pollution

    def get_input_additional_connector(self) -> ODHBaseConnector:
        return self._connector_collector.weather

    def get_output_connector(self) -> ODHBaseConnector:
        return self._connector_collector.pollution_dispersal

    def _get_data_types(self) -> List[DataType]:
        return PollutionDispersalMeasure.get_data_types()

    def _build_from_entries(self, input_entries: List[PollutionDispersalEntry]) -> MeasureCollection:
        return PollutionDispersalMeasureCollection.build_from_entries(input_entries, self._provenance)

    def _download_pollution_data(self,
                                   from_date: datetime,
                                   to_date: datetime,
                                   ) -> PollutionMeasureCollection:
        """
        Download pollution data measures in the given interval.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting PollutionMeasureCollection containing the pollution data.
        """

        connector = self.get_input_connector()
        logger.info(f"Downloading pollution data from [{from_date}] to [{to_date}]")
        nox_pollutants = PollutionMeasure.get_data_types([PollutantClass.NOx])
        # TODO: instead of downloading data for all stations (and then filter out by station id),
        #       download data for each station independently?
        return PollutionMeasureCollection(
            measures=connector.get_measures(from_date=from_date, to_date=to_date, measure_types=list(map(lambda x: x.name, nox_pollutants)))
        )

    def _download_weather_data(self, from_date: datetime, to_date: datetime) -> WeatherMeasureCollection:
        """
        Download weather data measures in the given interval.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting WeatherMeasureCollection containing the weather data.
        """

        connector = self.get_input_additional_connector()
        logger.info(f"Downloading weather data from [{from_date}] to [{to_date}]")
        # TODO: instead of downloading data for all stations (and then filter out by station id),
        #       download data for each station independently?
        return WeatherMeasureCollection(
            measures=connector.get_measures(from_date=from_date, to_date=to_date)
        )

    def _download_data_and_compute(self, stations: List[TrafficSensorStation]) -> Tuple[List[GenericEntry], List[Station]]:

        if len(stations) < 1:
            logger.error(f"Cannot compute pollution dispersal on empty station list ({len(stations)} passed)")
            return [], []

        start_date = datetime.now()  # TODO: localize?
        start_date = datetime(2020, 1, 1, 0)  # TODO: remove
        to_date = start_date + timedelta(hours=DAG_POLLUTION_DISPERSAL_TRIGGER_DAG_HOURS_SPAN)
        logger.info(f"Computing pollution dispersal from {start_date} to {to_date} for stations {stations}")

        pollution_data = None
        weather_data = None
        try:
            pollution_data = self._download_pollution_data(start_date, to_date)
            weather_data = self._download_weather_data(start_date, to_date)
            # TODO: add the possibility to retrieve also the `RoadWeather` stations

        except Exception as e:
            logger.exception(
                f"Unable to download pollution and weather data for stations {stations}",
                exc_info=e)

        if pollution_data and weather_data:
            logger.info(f"Length of pollution data: {len(pollution_data.measures)}")
            logger.info(f"Length of weather data: {len(weather_data.measures)}")

            # Filtering pollution and weather data for only the stations present in the mapping
            pollution_data = PollutionMeasureCollection(list(filter(lambda x: x.station.code in [station.code for station in stations], pollution_data.measures)))
            logger.info(f"Length of pollution data after filtering: {len(pollution_data.measures)}")
            weather_data = WeatherMeasureCollection(list(filter(lambda x: x.station.code in [station.meteo_station_code for station in stations], weather_data.measures)))
            logger.info(f"Length of weather data after filtering: {len(weather_data.measures)}")

            # Check if there are stations for which no pollution or weather data is not available
            # Only for logging purposes
            total_weather_records_for_station = {station.meteo_station_code: len(list(filter(lambda x: x.station.code == station.meteo_station_code, weather_data.measures))) for station in stations}
            total_pollution_records_for_station = {}
            for station in stations:
                id_stazione = station.id_stazione
                if id_stazione not in total_pollution_records_for_station:
                    total_pollution_records_for_station[id_stazione] = 0
                total_pollution_records_for_station[id_stazione] += len(list(filter(lambda x: x.station.code == station.code, pollution_data.measures)))
            skipped_stations_for_pollutions = {station.id_stazione: station.meteo_station_code for station in stations if total_pollution_records_for_station[station.id_stazione] == 0}
            logger.info("No pollution data found for traffic stations: " + str(list(set(skipped_stations_for_pollutions.keys()))))
            skipped_stations_for_weathers = {station.id_stazione: station.meteo_station_code for station in stations if total_weather_records_for_station[station.meteo_station_code] == 0}
            logger.info("No weather data found for weather stations: " + str(list(set(skipped_stations_for_weathers.values()))))
            skipped_stations_for_pollutions.update(skipped_stations_for_weathers)
            logger.info("Skipped stations for absence of data: " + str(skipped_stations_for_pollutions))

            model = PollutionDispersalModel()
            return model.compute_data(pollution_data, weather_data, start_date)

        return [], []

    def run_computation_for_multiple_stations(self, stations: List[TrafficSensorStation]) -> None:
        """
        Run the computation for multiple stations.

        :param stations: The list of stations to compute.
        """
        entries, dispersal_stations = self._download_data_and_compute(stations)
        logger.info(f"Computed {len(entries)} pollution dispersal entries")
        # TODO: upload pollution dispersal stations?
        # self._upload_data(entries)
