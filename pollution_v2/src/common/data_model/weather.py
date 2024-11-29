# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Iterator, Optional

from common.data_model import Station, TrafficSensorStation
from common.data_model.common import VehicleClass, MeasureCollection, Measure, DataType
from common.data_model.entry import GenericEntry
from common.settings import DATATYPE_PREFIX


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
                DataType(f"{DATATYPE_PREFIX}{weather_measure.name}", f"{weather_measure.value}", "total", "-", {})
            )
        return data_types


@dataclass
class WeatherEntry(GenericEntry):

    def __init__(self, station: TrafficSensorStation, valid_time: datetime, period: Optional[int],
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
        # TODO: implement
        pass

    def _get_entries_iterator(self) -> Iterator[WeatherEntry]:
        """
        Build and retrieve the iterator for list of weather entry from the available measures

        :return: an iterator of weather entries
        """
        for station_dict in self._build_entries_dictionary().values():
            for date_dict in station_dict.values():
                for weather_entry in date_dict.values():
                    yield weather_entry

    def get_entries(self) -> List[WeatherEntry]:
        """
        Build and retrieve the list of weather entry from the available measures

        :return: a list of weather entries
        """
        return list(self._get_entries_iterator())
