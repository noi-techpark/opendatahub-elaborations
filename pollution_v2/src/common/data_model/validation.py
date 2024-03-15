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
from common.data_model.traffic import TrafficSensorStation


class ValidationTypeClass(Enum):
    # single enum class to prevent further types additions
    VALID = "VALID"


@dataclass
class ValidationEntry(GenericEntry):

    def __init__(self, station: TrafficSensorStation, valid_time: datetime, vehicle_class: VehicleClass,
                 entry_class: ValidationTypeClass, entry_value: Optional[float], period: Optional[int]):
        super().__init__(station, valid_time, vehicle_class, entry_value, period)
        self.entry_class = entry_class


class ValidationMeasure(Measure):

    @staticmethod
    def get_data_types() -> List[DataType]:
        data_types = []
        for vehicle in VehicleClass:
            for validation_type in ValidationTypeClass:
                data_types.append(
                    DataType(f"{vehicle.name}-{validation_type.name}", f"{vehicle.value} is {validation_type.name}",
                             "Validation", "-", {}))
        return data_types


@dataclass
class ValidationMeasureCollection(MeasureCollection[ValidationMeasure, TrafficSensorStation]):

    @staticmethod
    def build_from_validation_entries(validation_entries: List[ValidationEntry],
                                      provenance: Provenance) -> ValidationMeasureCollection:
        """
        Build a ValidationMeasureCollection from the list of validation entries.

        :param validation_entries: the validation entries from which generate the ValidationMeasureCollection
        :param provenance: the provenance of the validation measures
        :return: a ValidationMeasureCollection object containing the validation measures generated from the validation entries
        """
        data_types_dict: Dict[str, DataType] = {data_type.name: data_type for data_type in
                                                ValidationMeasure.get_data_types()}
        validation_measures: List[ValidationMeasure] = []
        for validation_entry in validation_entries:
            validation_measures.append(ValidationMeasure(
                station=validation_entry.station,
                data_type=data_types_dict[
                    f"{validation_entry.vehicle_class.name}-{validation_entry.entry_class.name}"],
                provenance=provenance,
                period=validation_entry.period,
                transaction_time=None,
                valid_time=validation_entry.valid_time,
                value=validation_entry.entry_value
            ))

        return ValidationMeasureCollection(validation_measures)
