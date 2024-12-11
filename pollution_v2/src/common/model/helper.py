# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime
from typing import Iterable, Set, List

import pandas as pd
import json
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
    def get_observation_dataframe(observation_entries: Iterable[RoadWeatherObservationEntry]) -> pd.DataFrame:
        """
        Get a dataframe from the given observation entries. The resulting dataframe will have the following columns:
        time,station_code,prec_qta,stato_meteo,temp_aria,temp_rugiada,temp_suolo,vento_vel

        :param observation_entries: the observation entries
        :return: the observation dataframe
        """
        temp = []
        for entry in observation_entries:
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
        timestamp,station-type,station-id,air-temperature,air-humidity,wind-speed,wind-direction,global-radiation,precipitation

        :param weather_entries: the weather entries
        :return: the weather dataframe
        """
        temp = []
        for entry in weather_entries:
            temp.append({
                "timestamp": entry.valid_time.isoformat(),
                "station-type": entry.station.station_type,
                "station-id": entry.station.code,
                "air-temperature": entry.air_temperature,
                "air-humidity": entry.air_humidity,
                "wind-speed": entry.wind_speed,
                "wind-direction": entry.wind_direction,
                "global-radiation": entry.global_radiation,
                "precipitation": entry.precipitation
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

        # TODO: remove example station and entries

        # example_station = TrafficSensorStation(code="asdf", wrf_code="", meteo_station_code="", active=False, available=False, coordinates={}, metadata={}, name="", station_type="", origin="")
        #
        # example_pollution_entries = [
        #     PollutionEntry(example_station, datetime(2018, 1, 1, 0, 0), VehicleClass.LIGHT_VEHICLES, PollutantClass.NOx, 5.0, 600),
        #     PollutionEntry(example_station, datetime(2018, 1, 1, 0, 0), VehicleClass.HEAVY_VEHICLES, PollutantClass.NOx, 10.0, 600),
        #     PollutionEntry(example_station, datetime(2018, 1, 1, 0, 0), VehicleClass.BUSES, PollutantClass.NOx, 7.0, 600),
        #     PollutionEntry(example_station, datetime(2018, 1, 1, 0, 10), VehicleClass.LIGHT_VEHICLES, PollutantClass.NOx, 11.0, 600),
        #     PollutionEntry(example_station, datetime(2018, 1, 1, 0, 10), VehicleClass.HEAVY_VEHICLES, PollutantClass.NOx, 4.0, 600),
        #     PollutionEntry(example_station, datetime(2018, 1, 1, 0, 10), VehicleClass.BUSES, PollutantClass.NOx, 9.0, 600),
        #     PollutionEntry(example_station, datetime(2018, 1, 1, 0, 20), VehicleClass.LIGHT_VEHICLES, PollutantClass.NOx, 11.0, 600),
        #     PollutionEntry(example_station, datetime(2018, 1, 1, 0, 20), VehicleClass.HEAVY_VEHICLES, PollutantClass.NOx, 4.0, 600),
        #     PollutionEntry(example_station, datetime(2018, 1, 1, 0, 20), VehicleClass.BUSES, PollutantClass.NOx, 9.0, 600)
        # ]

        pollution_df = pd.DataFrame([{
            "timestamp": entry.valid_time.isoformat(),
            "station-id": entry.station.code,
            "pollutant": entry.entry_class.value,
            "vehicle_class": entry.vehicle_class.value.lower(),
            "pollution_value": entry.entry_value
        } for entry in pollution_entries])

        pollution_df = pollution_df.pivot_table(
            index=["timestamp", "station-id", "pollutant"],
            columns="vehicle_class",
            values="pollution_value",
            aggfunc="sum"
        ).reset_index().fillna(0)

        # if column 'buses', 'light_vehicles' or 'heavy_vehicles' is missing, add it with value 0
        for vehicle_class in ['buses', 'light_vehicles', 'heavy_vehicles']:
            if vehicle_class not in pollution_df.columns:
                pollution_df[vehicle_class] = 0

        return pollution_df
