# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import requests

from common.cache.common import TrafficManagerClass
from common.cache.computation_checkpoint import ComputationCheckpointCache
from common.connector.collector import ConnectorCollector
from common.connector.common import ODHBaseConnector
from common.data_model import Provenance, DataType, MeasureCollection, PollutionMeasureCollection, \
    PollutionDispersalMeasure, TrafficSensorStation, PollutionMeasure, PollutantClass, Station, \
    RoadWeatherObservationMeasureCollection, RoadWeatherObservationMeasureType
from common.data_model.entry import GenericEntry
from common.data_model.pollution_dispersal import PollutionDispersalEntry, PollutionDispersalMeasureCollection
from common.data_model.weather import WeatherMeasureCollection, WeatherMeasureType
from common.manager.station import StationManager
from common.settings import DAG_POLLUTION_DISPERSAL_TRIGGER_DAG_HOURS_SPAN, \
    POLLUTION_DISPERSAL_STATION_MAPPING_ENDPOINT, POLLUTION_DISPERSAL_STARTING_DATE
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

    def get_output_connector(self) -> ODHBaseConnector:
        return self._connector_collector.pollution_dispersal

    def _get_data_types(self) -> List[DataType]:
        return PollutionDispersalMeasure.get_data_types()

    def _build_from_entries(self, input_entries: List[PollutionDispersalEntry]) -> MeasureCollection:
        return PollutionDispersalMeasureCollection.build_from_entries(input_entries, self._provenance)

    def _download_pollution_data(self, from_date: datetime, to_date: datetime, stations: List[TrafficSensorStation])\
                                 -> PollutionMeasureCollection:
        """
        Download pollution data measures in the given interval.
        Filters only data for the given stations.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting PollutionMeasureCollection containing the pollution data.
        """

        connector = self.get_input_connector()
        logger.info(f"Downloading pollution data from [{from_date}] to [{to_date}]")
        nox_pollutants = PollutionMeasure.get_data_types([PollutantClass.NOx])
        measures = connector.get_measures(from_date=from_date, to_date=to_date, measure_types=list(map(lambda x: x.name, nox_pollutants)))
        station_codes = [s.code for s in stations]
        measures = filter(lambda x: x.station.code in station_codes, measures)
        return PollutionMeasureCollection(measures=list(measures))

    def _download_weather_data(self, from_date: datetime, to_date: datetime, stations: List[TrafficSensorStation])\
                               -> WeatherMeasureCollection:
        """
        Download weather data measures in the given interval. Filters only data for the given stations.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting WeatherMeasureCollection containing the weather data.
        """

        connector = self._connector_collector.weather
        logger.info(f"Downloading weather data from [{from_date}] to [{to_date}]")
        measure_types = [
            WeatherMeasureType.AIR_TEMPERATURE, WeatherMeasureType.AIR_HUMIDITY, WeatherMeasureType.WIND_SPEED,
            WeatherMeasureType.WIND_DIRECTION, WeatherMeasureType.GLOBAL_RADIATION
        ]
        measures = connector.get_measures(from_date=from_date, to_date=to_date, measure_types=[mt.value for mt in measure_types])
        station_codes = [s.meteo_station_code for s in stations]
        weather_station_type = self._connector_collector.weather._station_type
        measures = filter(lambda x: x.station.code in station_codes and x.station.station_type == weather_station_type,measures)
        return WeatherMeasureCollection(measures=list(measures))

    def _download_road_weather_data(self, from_date: datetime, to_date: datetime, stations: List[TrafficSensorStation])\
                                    -> RoadWeatherObservationMeasureCollection:
        """
        Download road weather data measures in the given interval. Filters only data for the given stations.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting WeatherMeasureCollection containing the weather data.
        """

        connector = self._connector_collector.road_weather_observation
        logger.info(f"Downloading road weather observation data from [{from_date}] to [{to_date}]")
        measure_types = [
            RoadWeatherObservationMeasureType.TEMP_ARIA, RoadWeatherObservationMeasureType.UMIDITA_REL,
            RoadWeatherObservationMeasureType.VENTO_VEL, RoadWeatherObservationMeasureType.VENTO_DIR,
        ]
        measures = connector.get_measures(from_date=from_date, to_date=to_date, measure_types=[mt.value for mt in measure_types])
        station_codes = [s.meteo_station_code for s in stations]
        road_weather_station_type = self._connector_collector.road_weather_observation._station_type
        measures = filter(lambda x: x.station.code in station_codes and x.station.station_type == road_weather_station_type, measures)
        return RoadWeatherObservationMeasureCollection(measures=list(measures))

    def _download_data_and_compute(self, stations: List[TrafficSensorStation]) -> Tuple[List[GenericEntry], List[Station], str]:
        """
        Download pollution and weather data for the given stations and compute pollution dispersal.

        :param stations: The list of stations to compute.
        :return: A tuple with the computed entries, the computed stations and the zip file name to upload.
        """

        if len(stations) < 1:
            logger.error(f"Cannot compute pollution dispersal on empty station list ({len(stations)} passed)")
            return [], [], ""

        start_date = POLLUTION_DISPERSAL_STARTING_DATE
        to_date = start_date + timedelta(hours=DAG_POLLUTION_DISPERSAL_TRIGGER_DAG_HOURS_SPAN)
        logger.info(f"Computing pollution dispersal from {start_date} to {to_date} for stations {stations}")

        pollution_data = None
        weather_data = None
        road_weather_data = None
        try:
            pollution_data = self._download_pollution_data(start_date, to_date, stations)
            weather_data = self._download_weather_data(start_date, to_date, stations)
            road_weather_data = self._download_road_weather_data(start_date, to_date, stations)

        except Exception as e:
            logger.exception(
                f"Unable to download pollution and weather data for stations {stations}",
                exc_info=e)

        if pollution_data and (weather_data or road_weather_data):

            domain_mapping = self._get_domain_mapping()

            skipped_domains = self._log_skipped_domains(pollution_data, weather_data, road_weather_data, stations, domain_mapping)

            expected_domains = set(domain_mapping.keys()) - skipped_domains
            model = PollutionDispersalModel(domain_mapping, expected_domains, self._connector_collector.pollution_dispersal)
            folder_name = model.compute_data(pollution_data, weather_data, road_weather_data, start_date)
            computed_entries, computed_stations = model.get_pollution_dispersal_entries_from_folder(folder_name)

            # remove folder and its files
            shutil.rmtree(folder_name)

            zip_file_to_upload = folder_name + ".zip"

            return computed_entries, computed_stations, zip_file_to_upload

        return [], [], ""

    def _get_domain_mapping(self) -> dict:
        # Retrieve the list of domain mappings from the ws
        response = requests.get(POLLUTION_DISPERSAL_STATION_MAPPING_ENDPOINT)
        if response.status_code != 200:
            logger.error(f"Failed to retrieve domain mapping: {response.status_code} {response.text}")
            raise ValueError(f"Failed to retrieve domain mapping: {response.status_code} {response.text}")
        logger.info(f"Retrieved domain mapping: {response.text}")
        return response.json()

    def _log_skipped_domains(self, pollution_data, weather_data, road_weather_data, stations, domain_mapping) -> set[str]:
        """
        Log the skipped weather and pollution data for the given stations.
        Also log the skipped domains.
        """

        logger.info(f"Length of pollution data for given stations: {len(pollution_data.measures)}")
        logger.info(f"Length of weather data for given stations: {len(weather_data.measures)}")
        logger.info(f"Length of road weather data for given stations: {len(road_weather_data.measures)}")

        # Check if there are stations for which no pollution or weather data is not available
        # Only for logging purposes
        skipped_pollution_stations = set()
        skipped_weather_stations = set()
        weather_station_type = self._connector_collector.weather._station_type
        road_weather_station_type = self._connector_collector.road_weather_observation._station_type
        for station in stations:
            pollution_data_for_station = list(filter(lambda x: x.station.code == station.code, pollution_data.measures))
            weather_data_for_station = list(filter(lambda x: x.station.code == station.meteo_station_code and x.station.station_type == weather_station_type, weather_data.measures))
            road_weather_data_for_station = list(filter(lambda x: x.station.code == station.meteo_station_code and x.station.station_type == road_weather_station_type, road_weather_data.measures))
            if len(pollution_data_for_station) == 0:
                skipped_pollution_stations.add(str(station.id_stazione))
            if len(weather_data_for_station) == 0 and len(road_weather_data_for_station) == 0:
                skipped_weather_stations.add(str(station.meteo_station_code))
        logger.info(f"Pollution stations with no data found: {skipped_pollution_stations}")
        logger.info(f"Weather and road weather stations with no data found: {skipped_weather_stations}")

        skipped_domains = set()
        for domain_id, domain in domain_mapping.items():
            if domain.get('traffic_station_id') in skipped_pollution_stations:
                skipped_domains.add(str(domain_id))
            elif domain.get('weather_station_id') in skipped_weather_stations:
                skipped_domains.add(str(domain_id))
        logger.info(f"Skipped domains: {skipped_domains}")
        return skipped_domains

    def run_computation_for_multiple_stations(self, stations: List[TrafficSensorStation]) -> None:
        """
        Run the computation for multiple stations.

        :param stations: The list of stations to compute.
        """
        entries, dispersal_stations, zip_file_name = self._download_data_and_compute(stations)

        if dispersal_stations:
            logger.info(f"Uploading environment stations: {len(dispersal_stations)}")
            self.get_output_connector().post_stations(dispersal_stations, self._provenance)
        else:
            logger.info("No pollution dispersal stations to upload")

        if entries:
            logger.info(f"Uploading pollution dispersal entries: {len(entries)}")
            self._upload_data(entries)
        else:
            logger.info("No pollution dispersal entries to upload")

        if zip_file_name:
            logger.info(f"Uploading pollution dispersal zip file: {zip_file_name}")
            # TODO: upload pollution dispersal zip file

            os.remove(zip_file_name)
        else:
            logger.info("No pollution dispersal zip file to upload")
