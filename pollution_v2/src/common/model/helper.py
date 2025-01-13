# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime
from typing import Iterable, Set, List

import pandas as pd
import json
import mimetypes
import logging

from common.data_model import TrafficSensorStation, RoadWeatherObservationEntry, PollutionEntry, VehicleClass, \
    PollutantClass
from common.data_model.history import HistoryEntry
from common.data_model.traffic import TrafficEntry
from common.data_model.weather import WeatherEntry

logger = logging.getLogger("pollution_v2.common.model")


class ModelHelper:
    """
    Created Pandas dataframes starting useful to feed computation algorithms
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
    def get_stations_dataframe(stations: List[TrafficSensorStation]) -> pd.DataFrame:
        """
        Get a dataframe from the given list of traffic stations.
        The resulting dataframe will have the following columns:
        station,km

        :param stations: the stations
        :return: the station dataframe
        """
        temp = []
        for entry in stations:
            if entry.km > 0:
                temp.append({
                    "station_id": entry.id_stazione,
                    "station_code": entry.code,
                    "km": entry.km,
                    "station_type": entry.station_type
                })

        return pd.DataFrame(temp)

    @staticmethod
    def get_traffic_dataframe(traffic_entries: Iterable[TrafficEntry],
                              date_filter: Set[datetime] = None) -> pd.DataFrame:
        """
        Get a dataframe from the given traffic entries. The resulting dataframe will have the following columns:
        date,time,Location,Station,Lane,Category,Transits,Speed,km

        :param traffic_entries: the traffic entries
        :param date_filter: the dates to filter on
        :return: the traffic dataframe
        """
        temp = []
        for entry in traffic_entries:

            km = None
            if "a22_metadata" in entry.station.metadata:
                try:
                    meta: dict = json.loads(entry.station.metadata["a22_metadata"])
                    km = meta.get("metro")
                except Exception as e:
                    logger.warning(f"Unable to parse the KM data for station [{entry.station.code}], error [{e}]")

            if date_filter is None or (date_filter is not None and entry.valid_time in date_filter):
                temp.append({
                    "date": entry.valid_time.date().isoformat(),
                    "time": entry.valid_time.time().isoformat(),
                    "Location": entry.station.id_strada,
                    "Station": entry.station.id_stazione,
                    "Lane": entry.station.id_corsia,
                    "Category": entry.vehicle_class.value,
                    "Transits": entry.nr_of_vehicles,
                    "Speed": entry.average_speed,
                    "Period": entry.period,
                    "KM": km
                })

        return pd.DataFrame(temp)

    @staticmethod
    def get_traffic_dataframe_for_validation(traffic_entries: Iterable[TrafficEntry], date: date) -> pd.DataFrame:
        """
        Get a dataframe from the given traffic entries. The resulting dataframe will have the following columns:
        time,value,station_code,variable

        :param traffic_entries: the traffic entries
        :param date: the date to filter on
        :return: the traffic dataframe
        """
        temp = []
        for entry in traffic_entries:
            if date == entry.valid_time.date():
                temp.append({
                    "time": entry.valid_time.time().isoformat(),
                    "value": entry.nr_of_vehicles,
                    "station_code": entry.station.code,
                    "variable": entry.vehicle_class.value
                })

        return pd.DataFrame(temp)

    @staticmethod
    def get_history_dataframe(history_entries: Iterable[HistoryEntry], date: date) -> pd.DataFrame:
        """
        Get a dataframe from the given history entries. The resulting dataframe will have the following columns:
        date,station_code,total_traffic

        :param history_entries: the history entries
        :param date: the date to filter on
        :return: the history dataframe
        """
        temp = []
        for entry in history_entries:
            temp.append({
                "date": entry.valid_time.date().isoformat(),
                "station_code": entry.station.code,
                "total_traffic": entry.nr_of_vehicles
            })

        return pd.DataFrame(temp)

    @staticmethod
    def get_weather_dataframe(weather_entries: Iterable[WeatherEntry]) -> pd.DataFrame:
        """
        Get a dataframe from the given weather entries. The resulting dataframe will have the following columns:
        timestamp,station-type,station-id,air-temperature,air-humidity,wind-speed,wind-direction,global-radiation

        :param weather_entries: the weather entries
        :return: the weather dataframe
        """
        temp = []
        for entry in weather_entries:
            temp.append({
                "timestamp": entry.valid_time.isoformat(),
                "station-type": 'Weather',
                "station-id": entry.station.code,
                "air-temperature": entry.air_temperature,
                "air-humidity": entry.air_humidity,
                "wind-speed": entry.wind_speed,
                "wind-direction": entry.wind_direction,
                "global-radiation": entry.global_radiation,
            })
        return pd.DataFrame(temp)

    @staticmethod
    def get_road_weather_dataframe(road_weather_entries: Iterable[RoadWeatherObservationEntry]) -> pd.DataFrame:
        """
        Get a dataframe from the given road weather entries. The resulting dataframe will have the following columns:
        timestamp,station-type,station-id,air-temperature,air-humidity,wind-speed,wind-direction,global-radiation

        :param road_weather_entries: the road weather entries
        :return: the weather dataframe
        """
        temp = []
        for entry in road_weather_entries:
            temp.append({
                "timestamp": entry.valid_time.isoformat(),
                "station-type": 'RoadWeather',
                "station-id": entry.station.code,
                "air-temperature": entry.temp_aria,
                "air-humidity": entry.umidita_rel,
                "wind-speed": entry.vento_vel,
                "wind-direction": entry.vento_dir,
                "global-radiation": "",  # global radiation is not present in ODH data for road weather stations
            })
        return pd.DataFrame(temp)

    @staticmethod
    def get_pollution_dataframe(pollution_entries: Iterable[PollutionEntry]) -> pd.DataFrame:
        """
        Get a dataframe from the given pollution entries. The resulting dataframe will have the following columns:
        timestamp,station-id,pollutant,light_vehicles,heave_vehicles,buses

        :param pollution_entries: the pollution entries
        :return: the pollution dataframe
        """

        pollution_df = pd.DataFrame([{
            "timestamp": entry.valid_time.isoformat(),
            "station-id": TrafficSensorStation.split_station_code(entry.station.code)[1],
            "pollutant": entry.entry_class.value,
            "vehicle_class": entry.vehicle_class.value.lower(),
            "pollution_value": entry.entry_value
        } for entry in pollution_entries])

        pollution_df = pollution_df.pivot_table(
            index=["timestamp", "station-id", "pollutant"],
            columns="vehicle_class",
            values="pollution_value",
            aggfunc="sum"
        ).reset_index().fillna(0)  # TODO: check if fillna(0) is correct

        # aggregate the pollution values by station.stazione_id
        pollution_df = pollution_df.groupby(["timestamp", "station-id"]).sum().reset_index()

        # if column 'buses', 'light_vehicles' or 'heavy_vehicles' is missing, add it with value 0
        for vehicle_class in ['buses', 'light_vehicles', 'heavy_vehicles']:
            if vehicle_class not in pollution_df.columns:
                pollution_df[vehicle_class] = 0

        return pollution_df
