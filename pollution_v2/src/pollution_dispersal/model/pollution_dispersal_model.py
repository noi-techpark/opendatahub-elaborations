# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
import mimetypes
import os
import time
import urllib.request
import zipfile
from datetime import datetime
from typing import List, Dict

import pandas as pd

from common.data_model.pollution import PollutionEntry, PollutionMeasureCollection
from common.data_model import TrafficSensorStation
from common.data_model.pollution_dispersal import PollutionDispersalEntry, PollutionDispersalMeasureType
from common.data_model.weather import WeatherMeasureCollection
from common.model.helper import ModelHelper
from common.settings import TMP_DIR, POLLUTION_DISPERSAL_PREDICTION_ENDPOINT, PERIOD_1HOUR

logger = logging.getLogger("pollution_v2.pollution_connector.model.pollution_dispersal_model")


class PollutionDispersalModel:
    """
    The model for computing pollution data.
    """

    @classmethod
    def create_multipart_formdata(cls, files):

        boundary = '----------Boundary'
        lines = []
        for filename in files:
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            lines.append(f'--{boundary}'.encode())
            lines.append(f'Content-Disposition: form-data; name="files"; filename="{filename}"'.encode())
            lines.append(f'Content-Type: {content_type}'.encode())
            lines.append(''.encode())
            with open(filename, 'rb') as f:
                lines.append(f.read())
        lines.append(f'--{boundary}--'.encode())
        lines.append(''.encode())
        body = b'\r\n'.join(lines)
        return body, boundary

    @staticmethod
    def _get_pollution_dispersal_entries_from_folder(folder_name: str, stations: List[TrafficSensorStation]) -> List[PollutionDispersalEntry]:

        station_mapping = {str(station.id_stazione): station for station in stations}

        # Iterate through each folder (station) and read the CSV files
        entries = []
        print("Iterating through each folder: ", os.listdir(folder_name))  # TODO: remove
        for file_name in os.listdir(folder_name):
            file_path = os.path.join(folder_name, file_name)
            if os.path.isdir(file_path) and file_name in station_mapping:
                station_id = file_name
                csv_file = os.path.join(file_path, f"{station_id}_output.csv")
                if os.path.isfile(csv_file):
                    df = pd.read_csv(csv_file)
                    for _, row in df.iterrows():
                        entries.append(PollutionDispersalEntry(
                            station=station_mapping[station_id],
                            valid_time=datetime.now(),
                            x_coordinate=row[PollutionDispersalMeasureType.X_COORDINATE.value],
                            y_coordinate=row[PollutionDispersalMeasureType.Y_COORDINATE.value],
                            z_coordinate=row[PollutionDispersalMeasureType.Z_COORDINATE.value],
                            c_a22=row[PollutionDispersalMeasureType.C_A22.value],
                            period=PERIOD_1HOUR
                        ))
        return entries

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
    def _ws_prediction(pollution_filename: str, weather_filename: str, start_date: datetime,
                       stations: List[TrafficSensorStation]) -> List[PollutionDispersalEntry]:
        formatted_dt = start_date.strftime("%Y-%m-%d-%H")
        url = f"{POLLUTION_DISPERSAL_PREDICTION_ENDPOINT}{formatted_dt}"
        logger.info(f"Sending prediction request to {url}")
        logger.info(f"Pollution file: {pollution_filename}")
        logger.info(f"Weather file: {weather_filename}")

        # List of files to upload
        files_to_upload = [pollution_filename, weather_filename]

        # Create multipart form data
        body, boundary = PollutionDispersalModel.create_multipart_formdata(files_to_upload)

        # Create a request object
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

        response_data = None
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
            return []

        return PollutionDispersalModel._get_pollution_dispersal_entries_from_folder(folder_name, stations)

    def compute_data(self, pollution: PollutionMeasureCollection, weather: WeatherMeasureCollection,
                     start_date: datetime, stations: List[TrafficSensorStation]) -> List[PollutionDispersalEntry]:

        pollution_data_types = {str(measure.data_type) for measure in pollution.measures}
        weather_data_types = {str(measure.data_type) for measure in weather.measures}

        logger.info(f"{len(pollution.measures)} pollution measures available "
                    f"on {len(pollution_data_types)} data types")
        logger.info(f"{len(weather.measures)} weather measures available "
                    f"on {len(weather_data_types)} data types")

        weather_entries = weather.get_entries()
        pollution_entries = pollution.get_entries()

        if len(weather_entries) > 0 and len(pollution_entries) > 0:
            weather_df = ModelHelper.get_weather_dataframe(weather_entries)
            pollution_df = ModelHelper.get_pollution_dataframe(pollution_entries)

            pollution_filename = self._create_temp_pollution_csv(pollution_df)
            weather_filename = self._create_temp_weather_csv(weather_df)

            return self._ws_prediction(pollution_filename, weather_filename, start_date, stations)

        else:
            logger.info(f"Not enough entries found (pollution: {len(pollution_entries)}, weather: {len(weather_entries)}), skipping computation")
            return []
