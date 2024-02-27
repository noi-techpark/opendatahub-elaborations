# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Iterator

import dateutil.parser

from common.data_model.common import VehicleClass, Measure, MeasureCollection, Station, DataType, \
    Provenance


@dataclass
class TrafficSensorStation(Station):

    def split_station_code(self) -> (str, int, int):
        """
        splits the station code using the pattern ID_strada:ID_stazione:ID_corsia and returns a tuple
        with the following structure (ID_strada, ID_stazione, ID_corsia)
        :return:
        """
        splits = self.code.split(":")
        if len(splits) != 3:
            raise ValueError(f"Unable to split [{self.code}] in ID_strada:ID_stazione:ID_corsia")
        return splits[0], int(splits[1]), int(splits[2])

    @property
    def id_strada(self) -> str:
        id_strada, id_stazione, id_corsia = self.split_station_code()
        return id_strada

    @property
    def id_stazione(self) -> int:
        id_strada, id_stazione, id_corsia = self.split_station_code()
        return id_stazione

    @property
    def id_corsia(self) -> int:
        id_strada, id_stazione, id_corsia = self.split_station_code()
        return id_corsia

    @classmethod
    def from_json(cls, dict_data) -> TrafficSensorStation:
        return TrafficSensorStation(
            code=dict_data["code"],
            active=dict_data["active"],
            available=dict_data["available"],
            coordinates=dict_data["coordinates"],
            metadata=dict_data["metadata"],
            name=dict_data["name"],
            station_type=dict_data["station_type"],
            origin=dict_data["origin"]
        )


@dataclass
class TrafficMeasure(Measure):
    station: TrafficSensorStation

    @classmethod
    def from_odh_repr(cls, raw_data: dict):
        return cls(
            station=TrafficSensorStation.from_odh_repr(raw_data),
            data_type=DataType.from_odh_repr(raw_data),
            provenance=Provenance.from_odh_repr(raw_data),
            period=raw_data.get("mperiod"),
            transaction_time=dateutil.parser.parse(raw_data["mtransactiontime"]) if raw_data.get("mtransactiontime") else None,
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
class TrafficEntry:
    station: TrafficSensorStation
    transaction_time: datetime
    valid_time: datetime
    vehicle_class: VehicleClass
    nr_of_vehicles: Optional[int]
    average_speed: Optional[float]
    period: Optional[int]


@dataclass
class TrafficMeasureCollection(MeasureCollection[TrafficMeasure, TrafficSensorStation]):

    def _build_traffic_entries_dictionary(self) -> Dict[str, Dict[datetime, Dict[VehicleClass, TrafficEntry]]]:
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
                    raise ValueError(f"Duplicated measure for type [{measure.data_type.name}] on station [{measure.station.code} for date [{measure.valid_time}]")
                entry.nr_of_vehicles = measure.value
            elif measure.is_average_speed_measure:
                if entry.average_speed is not None:
                    raise ValueError(f"Duplicated measure for type [{measure.data_type.name}] on station [{measure.station.code} for date [{measure.valid_time}]")
                entry.average_speed = measure.value

        return result

    def get_traffic_entries(self) -> Iterator[TrafficEntry]:
        """
        Build and retrieve the list of traffic entry from the available measures

        :return: an iterator of traffic entries
        """
        for station_dict in self._build_traffic_entries_dictionary().values():
            for date_dict in station_dict.values():
                for traffic_entry in date_dict.values():
                    yield traffic_entry
