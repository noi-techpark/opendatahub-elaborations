# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Iterator, List

import dateutil.parser

from common.data_model.common import VehicleClass, Measure, MeasureCollection, DataType, \
    Provenance
from common.data_model.entry import GenericEntry
from common.data_model.station import TrafficSensorStation


class TrafficMeasureType(Enum):

    NR_BUSES = "Nr. Buses"
    NR_HEAVY_VEHICLES = "Nr. Heavy Vehicles"
    NR_LIGHT_VEHICLES = "Nr. Light Vehicles"
    AVERAGE_SPEED_BUSES = "Average Speed Buses"
    AVERAGE_SPEED_HEAVY_VEHICLES = "Average Speed Heavy Vehicles"
    AVERAGE_SPEED_LIGHT_VEHICLES = "Average Speed Light Vehicles"


@dataclass
class TrafficMeasure(Measure):
    """
    Measure representing traffic.
    """

    station: TrafficSensorStation

    @classmethod
    def from_odh_repr(cls, raw_data: dict):
        return cls(
            station=TrafficSensorStation.from_odh_repr(raw_data),
            data_type=DataType.from_odh_repr(raw_data),
            provenance=Provenance.from_odh_repr(raw_data),
            period=raw_data.get("mperiod"),
            transaction_time=dateutil.parser.parse(raw_data["mtransactiontime"]) if raw_data.get(
                "mtransactiontime") else None,
            valid_time=dateutil.parser.parse(raw_data["mvalidtime"]),
            value=raw_data["mvalue"],
        )

    @property
    def vehicle_class(self):
        if "BUSES" in self.data_type.name.upper():
            return VehicleClass.BUSES
        elif "HEAVY" in self.data_type.name.upper():
            return VehicleClass.HEAVY_VEHICLES
        elif "LIGHT" in self.data_type.name.upper():
            return VehicleClass.LIGHT_VEHICLES

    @property
    def is_vehicle_counting_measure(self) -> bool:
        return self.data_type.name.upper() in [
            "NR. BUSES",
            "NR. HEAVY VEHICLES",
            "NR. LIGHT VEHICLES"
        ]

    @property
    def is_average_speed_measure(self) -> bool:
        return self.data_type.name.upper() in [
            "AVERAGE SPEED BUSES",
            "AVERAGE SPEED HEAVY VEHICLES",
            "AVERAGE SPEED LIGHT VEHICLES"
        ]


@dataclass
class TrafficEntry(GenericEntry):

    def __init__(self, station: TrafficSensorStation, transaction_time: datetime, valid_time: datetime,
                 vehicle_class: VehicleClass, nr_of_vehicles: Optional[int], average_speed: Optional[float], period: Optional[int]):
        super().__init__(station, valid_time, period)
        self.transaction_time = transaction_time
        self.vehicle_class = vehicle_class
        self.nr_of_vehicles = nr_of_vehicles
        self.average_speed = average_speed


@dataclass
class TrafficMeasureCollection(MeasureCollection[TrafficMeasure, TrafficSensorStation]):

    def _build_entries_dictionary(self) -> Dict[str, Dict[datetime, Dict[VehicleClass, TrafficEntry]]]:
        # A temporary dictionary used for faster aggregation of the results
        # The dictionary will have the following structure
        # StationCode -> (measure valid time -> (vehicle class -> TrafficEntry))
        result: Dict[str, Dict[datetime, Dict[VehicleClass, TrafficEntry]]] = {}
        for measure in self.measures:
            if measure.station.code not in result:
                result[measure.station.code] = {}
            if measure.valid_time not in result[measure.station.code]:
                result[measure.station.code][measure.valid_time] = {}
            if measure.vehicle_class not in result[measure.station.code][measure.valid_time]:
                entry = TrafficEntry(
                    station=measure.station,
                    transaction_time=measure.transaction_time,
                    valid_time=measure.valid_time,
                    vehicle_class=measure.vehicle_class,
                    nr_of_vehicles=None,
                    average_speed=None,
                    period=measure.period
                )
                result[measure.station.code][measure.valid_time][measure.vehicle_class] = entry
            else:
                entry = result[measure.station.code][measure.valid_time][measure.vehicle_class]

            if measure.is_vehicle_counting_measure:
                if entry.nr_of_vehicles is not None:
                    raise ValueError(
                        f"Duplicated measure for type [{measure.data_type.name}] "
                        f"on station [{measure.station.code}] for date [{measure.valid_time}]")
                entry.nr_of_vehicles = measure.value
            elif measure.is_average_speed_measure:
                if entry.average_speed is not None:
                    raise ValueError(
                        f"Duplicated measure for type [{measure.data_type.name}] "
                        f"on station [{measure.station.code}] for date [{measure.valid_time}]")
                entry.average_speed = measure.value

        return result

    def _get_entries_iterator(self) -> Iterator[TrafficEntry]:
        """
        Build and retrieve the iterator for list of traffic entry from the available measures

        :return: an iterator of traffic entries
        """
        for station_dict in self._build_entries_dictionary().values():
            for date_dict in station_dict.values():
                for traffic_entry in date_dict.values():
                    yield traffic_entry

    def get_entries(self) -> List[TrafficEntry]:
        """
        Build and retrieve the list of traffic entry from the available measures

        :return: a list of traffic entries
        """
        return list(self._get_entries_iterator())
