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
import requests

from common.data_model.pollution import PollutionMeasureCollection
from common.data_model import Station
from common.data_model.pollution_dispersal import PollutionDispersalEntry
from common.data_model.weather import WeatherMeasureCollection
from common.model.helper import ModelHelper
from common.settings import TMP_DIR, POLLUTION_DISPERSAL_PREDICTION_ENDPOINT, PERIOD_1HOUR, \
    POLLUTION_DISPERSAL_STATION_MAPPING_ENDPOINT

logger = logging.getLogger("pollution_v2.pollution_connector.model.pollution_dispersal_model")


class PollutionDispersalModel:
    """
    The model for computing pollution data.
    """

    @staticmethod
    def _get_pollution_dispersal_entries_from_folder(folder_name: str) -> Tuple[List[PollutionDispersalEntry], List[Station]]:
        poi_file = os.path.join(folder_name, "poi.json")
        if not os.path.isfile(poi_file):
            logger.error(f"POI file not found: {poi_file}")
            return [], []

        # the poi file contains a list of dictionaries, decode it:
        with open(poi_file, "r") as f:
            pois = json.load(f)

        # Retrieve the list of domain mappings from the ws to get the domain descriptions
        response = requests.get(POLLUTION_DISPERSAL_STATION_MAPPING_ENDPOINT)
        if response.status_code != 200:
            logger.error(f"Failed to retrieve domain mapping: {response.status_code} {response.text}")
            raise ValueError(f"Failed to retrieve domain mapping: {response.status_code} {response.text}")
        logger.info(f"Retrieved domain mapping: {response.text}")
        domain_mapping = response.json()

        entries = []
        stations = []
        for poi in pois:
            domain_id = poi.get("domain_id")
            point_id = poi.get("point_id")
            # TODO: check
            station = Station(
                code=f"{domain_id}_{point_id}",
                name=domain_mapping.get(domain_id, {}).get("description", str(domain_id)) + f" - {point_id}",
                active=True,
                available=True,
                coordinates={
                    "x": poi.get("x"),
                    "y": poi.get("y"),
                    "srid": poi.get("epsg", "")
                },
                metadata={
                    "dist_from_source_[m]": poi.get("dist_from_source_[m]")
                },
                station_type="PollutionDispersal",
                origin=None,
                wrf_code=None,
                meteo_station_code=None,
            )
            stations.append(station)
            entries.append(PollutionDispersalEntry(
                valid_time=datetime.now(),
                station=station,
                concentration_value=poi.get("conc_value_[ug/m3]"),
                period=PERIOD_1HOUR,
            ))

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
    def _create_temp_weather_csv(weather_df: pd.DataFrame) -> str:

        weather_filename = f"{TMP_DIR}/weather_{round(time.time() * 1000)}.csv"
        with open(weather_filename, 'a') as tmp_csv:
            tmp_csv.write('timestamp,station-type,station-id,air-temperature,air-humidity,wind-speed,wind-direction,global-radiation,precipitation\n')
            for _, row in weather_df.iterrows():
                timestamp = row.loc['timestamp']
                station_type = row.loc['station-type']
                station_id = row.loc['station-id']
                temperature = row.loc['air-temperature']
                humidity = row.loc['air-humidity']
                wind_speed = row.loc['wind-speed']
                wind_direction = row.loc['wind-direction']
                radiation = row.loc['global-radiation']
                precipitation = row.loc['precipitation']
                tmp_csv.write(f'{timestamp},{station_type},{station_id},{temperature},{humidity},{wind_speed},{wind_direction},{radiation},{precipitation}\n')
        return weather_filename

    @staticmethod
    def _ws_prediction(pollution_filename: str, weather_filename: str, start_date: datetime) -> Tuple[List[PollutionDispersalEntry], List[Station]]:
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

                # Decode zip file sent in response
                zip_filename = f"{TMP_DIR}/pollution_dispersal_{time_str}.zip"
                with open(zip_filename, 'wb') as zip_file:
                    zip_file.write(response_data)

                folder_name = f"{TMP_DIR}/pollution_dispersal_{time_str}"
                os.makedirs(folder_name)
                with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                    zip_ref.extractall(folder_name)

        except Exception as e:
            logger.error(f"error while processing request: {e}")
            return [], []

        return PollutionDispersalModel._get_pollution_dispersal_entries_from_folder(folder_name)

    def compute_data(self, pollution: PollutionMeasureCollection, weather: WeatherMeasureCollection,
                     start_date: datetime) -> Tuple[List[PollutionDispersalEntry], List[Station]]:

        weather_entries = weather.get_entries()
        pollution_entries = pollution.get_entries()

        if len(weather_entries) > 0 and len(pollution_entries) > 0:
            weather_df = ModelHelper.get_weather_dataframe(weather_entries)
            pollution_df = ModelHelper.get_pollution_dataframe(pollution_entries)

            pollution_filename = self._create_temp_pollution_csv(pollution_df)
            weather_filename = self._create_temp_weather_csv(weather_df)

            return self._ws_prediction(pollution_filename, weather_filename, start_date)

        else:
            logger.info(f"Not enough entries found (pollution: {len(pollution_entries)}, weather: {len(weather_entries)}), skipping computation")
            return [], []
