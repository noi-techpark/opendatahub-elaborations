# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict

from common.data_model.common import VehicleClass, MeasureCollection, Measure, Provenance, DataType
from common.data_model.entry import GenericEntry
from common.data_model.station import TrafficSensorStation
from common.settings import DATATYPE_PREFIX


@dataclass
class PollutionEntry(GenericEntry):

    def __init__(self, station: TrafficSensorStation, valid_time: datetime, temp_aria: float, temp_suolo: float,
                 temp_rugiada: float, prec_qta: float, vento_vel: float, prec_tipo_desc: str, period: Optional[int]):
        super().__init__(station, valid_time, period)
        self.temp_aria = temp_aria
        self.temp_suolo = temp_suolo
        self.temp_rugiada = temp_rugiada
        self.prec_qta = prec_qta
        self.vento_vel = vento_vel
        self.prec_tipo_desc = prec_tipo_desc


class RoadWeatherObservationMeasure(Measure):
    """
    Measure representing road weather observation.
    """

    @staticmethod
    def get_data_types() -> List[DataType]:
        """
        Returns the data types specific for this measure.

        :return: the data types specific for this measure
        """
        data_types = [
            DataType(f"temp_aria", f"air temperature", "???", "ºC", {}),
            DataType(f"temp_suolo", f"surface temperature", "???", "ºC", {}),
            DataType(f"temp_rugiada", f"dew temperature", "???", "ºC", {}),
            DataType(f"prec_qta", f"precipitation quantity", "???", "mm", {}),
            DataType(f"vento_vel", f"wind velocity", "???", "km/h", {}),
            DataType(f"prec_tipo_desc", f"prec_tipo_desc", "???", "-", {}),
        ]
        return data_types


@dataclass
class RoadWeatherObservationMeasureCollection(MeasureCollection[RoadWeatherObservationMeasure, TrafficSensorStation]):

    pass
    # @staticmethod
    # def build_from_entries(observation_entries: List[PollutionEntry],
    #                        provenance: Provenance) -> RoadWeatherObservationMeasureCollection:
    #     """
    #     Build a RoadWeatherObservationMeasureCollection from the list of road weather observation entries.
    #
    #     :param observation_entries: the observation entries from which generate the RoadWeatherObservationMeasureCollection
    #     :param provenance: the provenance of the observation measures
    #     :return: a RoadWeatherObservationMeasureCollection object containing the observation measures generated from the observation entries
    #     """
    #     data_types_dict: Dict[str, DataType] = {data_type.name: data_type for data_type in RoadWeatherObservationMeasure.get_data_types()}
    #     observation_measures: List[RoadWeatherObservationMeasure] = []
    #     for observation_entry in observation_entries:
    #         observation_measures.append(RoadWeatherObservationMeasure(
    #             station=observation_entry.station,
    #             data_type=data_types_dict[f"{DATATYPE_PREFIX}{observation_entry.vehicle_class.name}-{observation_entry.entry_class.name}-emissions"],
    #             provenance=provenance,
    #             period=observation_entry.period,
    #             transaction_time=None,
    #             valid_time=observation_entry.valid_time,
    #             value=observation_entry.entry_value
    #         ))
    #
    #     return RoadWeatherObservationMeasureCollection(observation_measures)
