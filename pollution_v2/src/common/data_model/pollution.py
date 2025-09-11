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
from common.data_model.station import TrafficSensorStation
from common.settings import DATATYPE_PREFIX


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
    def get_data_types(pollutant_classes: list[PollutantClass] = None) -> List[DataType]:
        """
        Returns the data types specific for this measure.

        :return: the data types specific for this measure
        """
        data_types = []
        for vehicle in VehicleClass:
            for pollutant in PollutantClass:
                if pollutant_classes is None or pollutant in pollutant_classes:
                    data_types.append(DataType(f"{DATATYPE_PREFIX}{vehicle.name}-{pollutant.name}-emissions",
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
                data_type=data_types_dict[f"{DATATYPE_PREFIX}{pollution_entry.vehicle_class.name}-{pollution_entry.entry_class.name}-emissions"],
                provenance=provenance,
                period=pollution_entry.period,
                transaction_time=None,
                valid_time=pollution_entry.valid_time,
                value=pollution_entry.entry_value
            ))

        return PollutionMeasureCollection(pollution_measures)

    def _build_entries_iterator(self) -> Iterator[PollutionEntry]:
        # A temporary dictionary used for faster aggregation of the results
        result: Dict[str, Dict[datetime, Dict[str, PollutionEntry]]] = {}
        for measure in self.measures:
            station_code = TrafficSensorStation.split_station_code(measure.station.code)[1]
            if station_code not in result:
                result[station_code] = {}
            if measure.valid_time not in result[station_code]:
                result[station_code][measure.valid_time] = {}
            vehicle_class = measure.data_type.name[len(DATATYPE_PREFIX)::].split("-")[0]
            if vehicle_class not in result[station_code][measure.valid_time]:
                entry = PollutionEntry(
                    # Pollution measure collection is of type station even though both PollutionMeasureConnector and
                    # PollutionMeasureCollection are of type TrafficSensorStation.
                    # Add cast `station: TrafficSensorStation` to PollutionMeasure to remove the warning.
                    station=measure.station,
                    valid_time=measure.valid_time,
                    vehicle_class=VehicleClass(measure.data_type.name[len(DATATYPE_PREFIX)::].split("-")[0]),
                    entry_class=PollutantClass(measure.data_type.name.split("-")[1]),
                    entry_value=measure.value,
                    period=measure.period
                )
                result[station_code][measure.valid_time][vehicle_class] = entry
            else:
                # Summing up the pollution values for each lane of the station
                result[station_code][measure.valid_time][vehicle_class].entry_value += measure.value

        for station_dict in result.values():
            for entry in station_dict.values():
                for vehicle_class, vehicle_entry in entry.items():
                    yield vehicle_entry

    def get_entries(self) -> List[PollutionEntry]:
        """
        Build and retrieve the list of entries from the available measures

        :return: a list of entries
        """
        return list(self._build_entries_iterator())
