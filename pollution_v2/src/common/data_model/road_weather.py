# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from enum import Enum

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Iterator, Dict

from common.data_model.common import MeasureCollection, Measure
from common.data_model.entry import GenericEntry
from common.data_model.station import Station


class RoadWeatherObservationMeasureType(Enum):

    PREC_QTA = "prec_qta"
    STATO_METEO = "stato_meteo"
    TEMP_ARIA = "temp_aria"
    TEMP_RUGIADA = "temp_rugiada"
    TEMP_SOULO = "temp_suolo"
    VENTO_VEL = "vento_vel"


class RoadWeatherForecastMeasureType(Enum):

    # TODO: check if these are correct
    TEMP_ARIA = "temp_aria"
    TEMP_RUGIADA = "temp_rugiada"
    PREC_QTA = "prec_qta"
    NEVE_QTA = "neve_qta"
    VENTO_VEL = "vento_vel"
    PRESS_ATM = "press_atm"
    COPERTURA_NUVOLOSA = "copertura_nuvolosa"
    RAD_SOLARE = "rad_solare"
    RAD_INFRAROSSI = "rad_infrarossi"


@dataclass
class RoadWeatherObservationEntry(GenericEntry):

    def __init__(self, station: Station, valid_time: datetime, temp_aria: float, temp_suolo: float,
                 temp_rugiada: float, prec_qta: float, vento_vel: float, stato_meteo: int, period: Optional[int]):
        super().__init__(station, valid_time, period)
        self.temp_aria = temp_aria
        self.temp_suolo = temp_suolo
        self.temp_rugiada = temp_rugiada
        self.prec_qta = prec_qta
        self.vento_vel = vento_vel
        self.stato_meteo = stato_meteo


class RoadWeatherObservationMeasure(Measure):
    """
    Measure representing road weather observation.
    """
    pass


@dataclass
class RoadWeatherObservationMeasureCollection(MeasureCollection[RoadWeatherObservationMeasure, Station]):
    """
    Collection of road weather observation measures.
    """
    pass

    def get_entries(self) -> List[RoadWeatherObservationEntry]:
        """
        Build and retrieve the list of traffic entry from the available measures

        :return: a list of traffic entries
        """
        return list(self._get_entries_iterator())

    def _get_entries_iterator(self) -> Iterator[RoadWeatherObservationEntry]:
        """
        Build and retrieve the iterator for list of observation entries from the available measures

        :return: an iterator of traffic entries
        """
        for station_dict in self._build_entries_dictionary().values():
            for entry in station_dict.values():
                yield entry

    def _build_entries_dictionary(self) -> Dict[str, Dict[datetime, RoadWeatherObservationEntry]]:
        # A temporary dictionary used for faster aggregation of the results
        # The dictionary will have the following structure
        # StationCode -> (measure valid time -> (RoadWeatherObservationEntry))
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

        result: Dict[str, Dict[datetime, RoadWeatherObservationEntry]] = {}
        for group_by_station in tmp:
            if group_by_station not in result:
                result[group_by_station] = {}
            for group_by_time in tmp[group_by_station]:
                entry = tmp[group_by_station][group_by_time]
                result[group_by_station][group_by_time] = RoadWeatherObservationEntry(
                    station=stations[group_by_station],
                    valid_time=group_by_time,
                    period=1,
                    temp_aria=entry['temp_aria'],
                    temp_suolo=entry['temp_suolo'],
                    temp_rugiada=entry['temp_rugiada'],
                    prec_qta=entry['prec_qta'],
                    vento_vel=entry['vento_vel'],
                    stato_meteo=entry['stato_meteo']
                )

        return result


@dataclass
class RoadWeatherForecastEntry(GenericEntry):

    def __init__(self, station: Station, valid_time: datetime, temp_aria: float,
                 temp_rugiada: float, prec_qta: float, neve_qta: float, vento_vel: float, press_atm: float,
                 copertura_nuvolosa: float, rad_solare: float, rad_infrarossi: float, period: Optional[int]):
        super().__init__(station, valid_time, period)
        self.temp_aria = temp_aria
        self.temp_rugiada = temp_rugiada
        self.prec_qta = prec_qta  # TODO: check if this is correct
        self.neve_qta = neve_qta  # TODO: check if this is correct
        self.vento_vel = vento_vel
        self.press_atm = press_atm  # TODO: check if this is correct
        self.copertura_nuvolosa = copertura_nuvolosa  # TODO: check if this is correct
        self.rad_solare = rad_solare  # TODO: check if this is correct
        self.rad_infrarossi = rad_infrarossi  # TODO: check if this is correct


class RoadWeatherForecastMeasure(Measure):
    """
    Measure representing road weather forecast.
    """
    pass


@dataclass
class RoadWeatherForecastMeasureCollection(MeasureCollection[RoadWeatherForecastMeasure, Station]):
    """
    Collection of road weather forecast measures.
    """
    pass
