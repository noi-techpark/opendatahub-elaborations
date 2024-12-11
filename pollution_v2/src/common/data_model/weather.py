# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Iterator, Optional

from common.data_model import Station, TrafficSensorStation
from common.data_model.common import MeasureCollection, Measure, DataType
from common.data_model.entry import GenericEntry


class WeatherMeasureType(Enum):

    AIR_TEMPERATURE = 'air-temperature'
    AIR_HUMIDITY = 'air-humidity'
    WIND_SPEED = 'wind-speed'
    WIND_DIRECTION = 'wind-direction'
    GLOBAL_RADIATION = 'global-radiation'
    PRECIPITATION = 'precipitation'


class WeatherMeasure(Measure):
    """
    Measure representing a weather condition.
    """

    @staticmethod
    def get_data_types() -> List[DataType]:
        """
        Returns the data types specific for this measure.

        :return: the data types specific for this measure
        """
        data_types = []
        for weather_measure in WeatherMeasureType:
            data_types.append(
                DataType(f"{weather_measure.name}", f"{weather_measure.value}", "total", "-", {})
            )
        return data_types


@dataclass
class WeatherEntry(GenericEntry):

    def __init__(self, station: Station, valid_time: datetime, period: Optional[int],
                 air_temperature: float, air_humidity: float, wind_speed: float, wind_direction: float,
                 global_radiation: float, precipitation: float):
        super().__init__(station, valid_time, period)
        self.air_temperature = air_temperature
        self.air_humidity = air_humidity
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.global_radiation = global_radiation
        self.precipitation = precipitation


@dataclass
class WeatherMeasureCollection(MeasureCollection[WeatherMeasure, Station]):

    def _build_entries_dictionary(self) -> Dict:
        # A temporary dictionary used for faster aggregation of the results
        tmp: Dict[str, Dict[datetime, dict]] = {}
        stations: Dict[str, Station] = {}
        for measure in self.measures:
            if measure.station.code not in stations:
                stations[measure.station.code] = measure.station
            if measure.station.code not in tmp:
                tmp[measure.station.code] = {}
            if measure.valid_time not in tmp[measure.station.code]:
                tmp[measure.station.code][measure.valid_time] = {}
            tmp[measure.station.code][measure.valid_time][measure.data_type.name] = measure.value

        result: Dict[str, Dict[datetime, WeatherEntry]] = {}
        for group_by_station in tmp:
            if group_by_station not in result:
                result[group_by_station] = {}
            for group_by_time in tmp[group_by_station]:
                entry = tmp[group_by_station][group_by_time]
                result[group_by_station][group_by_time] = WeatherEntry(
                    station=stations[group_by_station],
                    valid_time=group_by_time,
                    period=1,
                    air_temperature=entry[WeatherMeasureType.AIR_TEMPERATURE.value] if WeatherMeasureType.AIR_TEMPERATURE.value in entry else "",
                    air_humidity=entry[WeatherMeasureType.AIR_HUMIDITY.value] if WeatherMeasureType.AIR_HUMIDITY.value in entry else "",
                    wind_speed=entry[WeatherMeasureType.WIND_SPEED.value] if WeatherMeasureType.WIND_SPEED.value in entry else "",
                    wind_direction=entry[WeatherMeasureType.WIND_DIRECTION.value] if WeatherMeasureType.WIND_DIRECTION.value in entry else "",
                    global_radiation=entry[WeatherMeasureType.GLOBAL_RADIATION.value] if WeatherMeasureType.GLOBAL_RADIATION.value in entry else "",
                    precipitation=entry[WeatherMeasureType.PRECIPITATION.value] if WeatherMeasureType.PRECIPITATION.value in entry else ""
                )

        return result

    def _get_entries_iterator(self) -> Iterator[WeatherEntry]:
        """
        Build and retrieve the iterator for list of weather entry from the available measures

        :return: an iterator of weather entries
        """
        for station_dict in self._build_entries_dictionary().values():
            for date_dict in station_dict.values():
                yield date_dict
                # for weather_entry in date_dict.values():
                #     yield weather_entry

    def get_entries(self) -> List[WeatherEntry]:
        """
        Build and retrieve the list of weather entry from the available measures

        :return: a list of weather entries
        """
        return list(self._get_entries_iterator())
