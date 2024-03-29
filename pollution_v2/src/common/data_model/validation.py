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

    def _build_entries_dictionary(self) -> Dict[str, Dict[datetime, Dict[VehicleClass, ValidationEntry]]]:
        # A temporary dictionary used for faster aggregation of the results
        # The dictionary will have the following structure
        # StationCode -> (measure valid time -> (vehicle class -> TrafficEntry))
        result: Dict[str, Dict[datetime, Dict[VehicleClass, ValidationEntry]]] = {}
        for measure in self.measures:
            if measure.station.code not in result:
                result[measure.station.code] = {}
            if measure.valid_time not in result[measure.station.code]:
                result[measure.station.code][measure.valid_time] = {}
            if measure.vehicle_class not in result[measure.station.code][measure.valid_time]:
                entry = ValidationEntry(
                    station=measure.station,
                    valid_time=measure.valid_time,
                    vehicle_class=measure.vehicle_class,
                    entry_class=None,
                    entry_value=None,
                    period=measure.period
                )
                result[measure.station.code][measure.valid_time][measure.vehicle_class] = entry
            else:
                entry = result[measure.station.code][measure.valid_time][measure.vehicle_class]

            if measure.is_vehicle_counting_measure:
                if entry.nr_of_vehicles is not None:
                    raise ValueError(
                        f"Duplicated measure for type [{measure.data_type.name}] on station [{measure.station.code} for date [{measure.valid_time}]")
                entry.nr_of_vehicles = measure.value
            elif measure.is_average_speed_measure:
                if entry.average_speed is not None:
                    raise ValueError(
                        f"Duplicated measure for type [{measure.data_type.name}] on station [{measure.station.code} for date [{measure.valid_time}]")
                entry.average_speed = measure.value

        return result

    # TODO unify on parent!
    def _get_entries_iterator(self) -> Iterator[TrafficEntry]:
        """
        Build and retrieve the iterator for list of traffic entry from the available measures

        :return: an iterator of traffic entries
        """
        for station_dict in self._build_entries_dictionary().values():
            for date_dict in station_dict.values():
                for traffic_entry in date_dict.values():
                    yield traffic_entry

    # TODO unify on parent!
    def get_entries(self) -> List[TrafficEntry]:
        """
        Build and retrieve the list of traffic entry from the available measures

        :return: a list of traffic entries
        """
        return list(self._get_entries_iterator())
