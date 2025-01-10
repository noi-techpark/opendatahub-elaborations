# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
import json
import os
import time
import urllib.request
import zipfile
from datetime import datetime
from typing import List, Tuple

import pandas as pd

from common.data_model.pollution import PollutionMeasureCollection
from common.data_model import Station, RoadWeatherObservationMeasureCollection
from common.data_model.pollution_dispersal import PollutionDispersalEntry
from common.data_model.weather import WeatherMeasureCollection
from common.model.helper import ModelHelper
from common.settings import TMP_DIR, POLLUTION_DISPERSAL_PREDICTION_ENDPOINT, PERIOD_1HOUR

logger = logging.getLogger("pollution_v2.pollution_connector.model.pollution_dispersal_model")


class PollutionDispersalModel:
    """
    The model for computing pollution data.
    """

    def __init__(self, domain_mapping: dict, expected_computed_domains: set):
        self.domain_mapping = domain_mapping
        self.expected_computed_domains = expected_computed_domains

    def get_pollution_dispersal_entries_from_folder(self, folder_name: str) -> Tuple[List[PollutionDispersalEntry], List[Station]]:
        """
        Get the pollution dispersal entries from a folder. The folder contains the POI.json file with the computed POIs.
        Returns a tuple with the pollution dispersal entries and the stations.

        :param folder_name: the folder name where the results are stored
        :return: a tuple with the pollution dispersal entries and the stations
        """
        poi_file = os.path.join(folder_name, "poi.json")
        if not os.path.isfile(poi_file):
            logger.error(f"POI file not found: {poi_file}")
            return [], []

        # the poi file contains a list of dictionaries, decode it:
        with open(poi_file, "r") as f:
            pois = json.load(f)

        entries = []
        stations = []
        computed_domains = set()
        for poi in pois:
            domain_id = poi.get("domain_id")
            point_id = poi.get("point_id")
            computed_domains.add(str(domain_id))
            # TODO: check
            station = Station(
                code=f"{domain_id}_{point_id}",
                name=self.domain_mapping.get(domain_id, {}).get("description", str(domain_id)) + f" - {point_id}",  # TODO: add description in capabilities endpoint
                active=True,
                available=True,
                coordinates={
                    "x": poi.get("x"),
                    "y": poi.get("y"),
                    "srid": poi.get("epsg", "")  # TODO: add `epsg` to the returned POIs
                },
                metadata={
                    "dist_from_source_[m]": poi.get("dist_from_source_[m]")
                },
                station_type="EnvironmentStation",
                origin="CISMA-dispersion-model",
                wrf_code=None,
                meteo_station_code=None,
            )
            stations.append(station)
            entry = PollutionDispersalEntry(
                valid_time=datetime.now(),
                station=station,
                concentration_value=poi.get("conc_value_[ug/m3]"),
                period=PERIOD_1HOUR,
            )
            entries.append(entry)

        # check if all expected domains have been computed
        if computed_domains != self.expected_computed_domains:
            logger.warning(f"Some domains have not been computed: {self.expected_computed_domains - computed_domains}")

        return entries, stations

    @staticmethod
    def _create_temp_pollution_csv(pollution_df: pd.DataFrame) -> str:

        pollution_filename = f"{TMP_DIR}/pollution_{round(time.time() * 1000)}.csv"
        with open(pollution_filename, 'a') as tmp_csv:
            tmp_csv.write('timestamp,station-id,pollutant,light_vehicles,heavy_vehicles,buses\n')
            for _, row in pollution_df.iterrows():
                timestamp = row.loc['timestamp']
                station_id = row.loc['station-id']
                pollutant = row.loc['pollutant']
                light_vehicles = row.loc['light_vehicles']
                heavy_vehicles = row.loc['heavy_vehicles']
                buses = row.loc['buses']
                tmp_csv.write(f'{timestamp},{station_id},{pollutant},{light_vehicles},{heavy_vehicles},{buses}\n')
        return pollution_filename

    @staticmethod
    def _create_temp_weather_csv(weather_df: pd.DataFrame, road_weather_df: pd.DataFrame) -> str:

        weather_filename = f"{TMP_DIR}/weather_{round(time.time() * 1000)}.csv"
        with open(weather_filename, 'a') as tmp_csv:
            tmp_csv.write('timestamp,station-type,station-id,air-temperature,air-humidity,wind-speed,wind-direction,global-radiation\n')
            for df in [weather_df, road_weather_df]:
                for _, row in df.iterrows():
                    timestamp = row.loc['timestamp']
                    station_type = row.loc['station-type']
                    station_id = row.loc['station-id']
                    temperature = row.loc['air-temperature']
                    humidity = row.loc['air-humidity']
                    wind_speed = row.loc['wind-speed']
                    wind_direction = row.loc['wind-direction']
                    radiation = row.loc['global-radiation']
                    tmp_csv.write(f'{timestamp},{station_type},{station_id},{temperature},{humidity},{wind_speed},{wind_direction},{radiation}\n')
        return weather_filename

    def _ws_prediction(self, pollution_filename: str, weather_filename: str, start_date: datetime) -> str:
        """
        Send a request to the pollution dispersal prediction service.
        Returns the folder name where the results are stored, also corresponds to the generated zip file name.

        :param pollution_filename: the name of the pollution file
        :param weather_filename: the name of the weather file
        :param start_date: the start date of the prediction
        :return: the folder name where the results are stored
        """
        formatted_dt = start_date.strftime("%Y-%m-%d-%H")
        url = f"{POLLUTION_DISPERSAL_PREDICTION_ENDPOINT}{formatted_dt}"
        logger.info(f"Sending prediction request to {url}")
        logger.info(f"Pollution file: {pollution_filename}")
        logger.info(f"Weather file: {weather_filename}")

        # List of files to upload
        files_to_upload = [pollution_filename, weather_filename]

        # Create multipart form data
        body, boundary = ModelHelper.create_multipart_formdata(files_to_upload)

        # Create a request object
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read()
                time_str = str(round(time.time() * 1000))
        except Exception as e:
            logger.error(f"error while processing request: {e}")
            return ""

        # Decode zip file sent in response
        zip_filename = f"{TMP_DIR}/pollution_dispersal_{time_str}.zip"
        with open(zip_filename, 'wb') as zip_file:
            zip_file.write(response_data)

        folder_name = f"{TMP_DIR}/pollution_dispersal_{time_str}"
        os.makedirs(folder_name)
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(folder_name)

        # Remove temporary files
        for file in files_to_upload:
            os.remove(file)

        return folder_name

    def compute_data(self, pollution: PollutionMeasureCollection, weather: WeatherMeasureCollection,
                     road_weather: RoadWeatherObservationMeasureCollection, start_date: datetime) -> str:
        """
        Compute the pollution dispersal data.
        Returns the folder name where the results are stored, also corresponds to the generated zip file name.

        :param pollution: the pollution data
        :param weather: the weather data
        :param road_weather: the road weather data
        :param start_date: the start date of the prediction
        :return: the folder name where the results are stored
        """

        weather_entries = weather.get_entries()
        pollution_entries = pollution.get_entries()
        road_weather_entries = road_weather.get_entries()

        if len(weather_entries) > 0 and len(pollution_entries) > 0:
            pollution_df = ModelHelper.get_pollution_dataframe(pollution_entries)
            weather_df = ModelHelper.get_weather_dataframe(weather_entries)
            road_weather_df = ModelHelper.get_road_weather_dataframe(road_weather_entries)

            pollution_filename = self._create_temp_pollution_csv(pollution_df)
            weather_filename = self._create_temp_weather_csv(weather_df, road_weather_df)
            return self._ws_prediction(pollution_filename, weather_filename, start_date)

        else:
            logger.info(f"Not enough entries found (pollution: {len(pollution_entries)}, weather: {len(weather_entries)}),"
                        f"road_weather: {len(road_weather_entries)}, skipping computation")
            return ""
