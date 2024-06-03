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


class PollutantClass(Enum):

    CO = "CO"
    CO2 = "CO2"
    NOx = "NOx"
    PM10 = "PM Exhaust"
    VOC = "VOC"


@dataclass
class PollutionEntry(GenericEntry):

    def __init__(self, station: TrafficSensorStation, valid_time: datetime, vehicle_class: VehicleClass,
                 entry_class: PollutantClass, entry_value: Optional[float], period: Optional[int]):
        super().__init__(station, valid_time, period)
        self.entry_class = entry_class
        self.vehicle_class = vehicle_class
        self.entry_value = entry_value


class PollutionMeasure(Measure):
    """
    Measure representing pollution.
    """

    @staticmethod
    def get_data_types() -> List[DataType]:
        """
        Returns the data types specific for this measure.

        :return: the data types specific for this measure
        """
        data_types = []
        for vehicle in VehicleClass:
            for pollutant in PollutantClass:
                data_types.append(DataType(f"{vehicle.name}-{pollutant.name}-emissions",
                                           f"{vehicle.value} emissions of {pollutant.name}", "total", "g/km", {}))
        return data_types


@dataclass
class PollutionMeasureCollection(MeasureCollection[PollutionMeasure, TrafficSensorStation]):

    @staticmethod
    def build_from_entries(pollution_entries: List[PollutionEntry],
                           provenance: Provenance) -> PollutionMeasureCollection:
        """
        Build a PollutionMeasureCollection from the list of pollution entries.

        :param pollution_entries: the pollution entries from which generate the PollutionMeasureCollection
        :param provenance: the provenance of the pollution measures
        :return: a PollutionMeasureCollection object containing the pollution measures generated from the pollution entries
        """
        data_types_dict: Dict[str, DataType] = {data_type.name: data_type for data_type in PollutionMeasure.get_data_types()}
        pollution_measures: List[PollutionMeasure] = []
        for pollution_entry in pollution_entries:
            pollution_measures.append(PollutionMeasure(
                station=pollution_entry.station,
                data_type=data_types_dict[f"{pollution_entry.vehicle_class.name}-{pollution_entry.entry_class.name}-emissions"],
                provenance=provenance,
                period=pollution_entry.period,
                transaction_time=None,
                valid_time=pollution_entry.valid_time,
                value=pollution_entry.entry_value
            ))

        return PollutionMeasureCollection(pollution_measures)
