# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from enum import Enum

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from common.data_model.common import MeasureCollection, Measure
from common.data_model.entry import GenericEntry
from common.data_model.station import TrafficSensorStation


class RoadWeatherObservationMeasureType(Enum):

    TEMP_ARIA = "temp_aria"
    TEMP_SOULO = "temp_suolo"
    TEMP_RUGIADA = "temp_rugiada"
    PREC_QTA = "prec_qta"
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

    def __init__(self, station: TrafficSensorStation, valid_time: datetime, temp_aria: float, temp_suolo: float,
                 temp_rugiada: float, prec_qta: float, vento_vel: float, period: Optional[int]):
        super().__init__(station, valid_time, period)
        self.temp_aria = temp_aria
        self.temp_suolo = temp_suolo
        self.temp_rugiada = temp_rugiada
        self.prec_qta = prec_qta
        self.vento_vel = vento_vel


class RoadWeatherObservationMeasure(Measure):
    """
    Measure representing road weather observation.
    """
    pass


@dataclass
class RoadWeatherObservationMeasureCollection(MeasureCollection[RoadWeatherObservationMeasure, TrafficSensorStation]):
    """
    Collection of road weather observation measures.
    """
    pass


@dataclass
class RoadWeatherForecastEntry(GenericEntry):

    def __init__(self, station: TrafficSensorStation, valid_time: datetime, temp_aria: float,
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
class RoadWeatherForecastMeasureCollection(MeasureCollection[RoadWeatherForecastMeasure, TrafficSensorStation]):
    """
    Collection of road weather forecast measures.
    """
    pass
