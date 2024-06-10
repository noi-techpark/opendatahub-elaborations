# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Iterator

from common.data_model.common import VehicleClass, MeasureCollection, Measure, Provenance, DataType
from common.data_model.entry import GenericEntry
from common.data_model.traffic import TrafficSensorStation, TrafficEntry
from common.settings import DATATYPE_PREFIX


class ValidationTypeClass(Enum):
    # single enum class to prevent further types additions
    VALID = "VALID"


@dataclass
class ValidationEntry(GenericEntry):

    def __init__(self, station: TrafficSensorStation, valid_time: datetime, vehicle_class: VehicleClass,
                 entry_class: ValidationTypeClass, entry_value: Optional[float], period: Optional[int]):
        super().__init__(station, valid_time, period)
        self.entry_class = entry_class
        self.vehicle_class = vehicle_class
        self.entry_value = entry_value


class ValidationMeasure(Measure):
    """
    Measure representing validation.
    """

    @staticmethod
    def get_data_types() -> List[DataType]:
        """
        Returns the data types specific for this measure.

        :return: the data types specific for this measure
        """
        data_types = []
        for vehicle in VehicleClass:
            for validation_type in ValidationTypeClass:
                data_types.append(
                    DataType(f"{DATATYPE_PREFIX}{vehicle.name}-{validation_type.name}", f"{vehicle.value} is {validation_type.name}",
                             "Validation", "-", {}))
        return data_types


@dataclass
class ValidationMeasureCollection(MeasureCollection[ValidationMeasure, TrafficSensorStation]):

    @staticmethod
    def build_from_entries(validation_entries: List[ValidationEntry],
                           provenance: Provenance, filter_is_valid=False) -> ValidationMeasureCollection:
        """
        Build a ValidationMeasureCollection from the list of validation entries.

        :param validation_entries: the validation entries from which generate the ValidationMeasureCollection
        :param provenance: the provenance of the validation measures
        :param filter_is_valid: if True, processes only the measure with is_valid set to True
        :return: a ValidationMeasureCollection object containing the validation measures generated from the validation entries
        """
        data_types_dict: Dict[str, DataType] = {data_type.name: data_type for data_type in
                                                ValidationMeasure.get_data_types()}
        validation_measures: List[ValidationMeasure] = []
        for validation_entry in validation_entries:
            if not filter_is_valid or (filter_is_valid and validation_entry.entry_value == 1):
                validation_measures.append(ValidationMeasure(
                    station=validation_entry.station,
                    data_type=data_types_dict[
                        f"{DATATYPE_PREFIX}{validation_entry.vehicle_class.name}-{validation_entry.entry_class.name}"],
                    provenance=provenance,
                    period=validation_entry.period,
                    transaction_time=None,
                    valid_time=validation_entry.valid_time,
                    value=validation_entry.entry_value
                ))

        return ValidationMeasureCollection(validation_measures)
