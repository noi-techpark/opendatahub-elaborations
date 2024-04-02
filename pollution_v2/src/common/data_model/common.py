# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import ast
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TypeVar, Generic, List, Optional, Dict, ClassVar

import dateutil.parser

import logging

logger = logging.getLogger("pollution_v2.common.data_model.common")


class VehicleClass(Enum):

    BUSES = "BUSES"
    HEAVY_VEHICLES = "HEAVY_VEHICLES"
    LIGHT_VEHICLES = "LIGHT_VEHICLES"


@dataclass
class Provenance:
    provenance_id: Optional[str]
    lineage: str
    data_collector: str
    data_collector_version: str

    @classmethod
    def from_odh_repr(cls, raw_data: dict):
        return cls(
            provenance_id=None,
            lineage=raw_data["prlineage"],
            data_collector=raw_data["prname"],
            data_collector_version=raw_data["prversion"]
        )

    def to_odh_repr(self) -> dict:
        return {
            "uuid": self.provenance_id,
            "lineage": self.lineage,
            "dataCollector": self.data_collector,
            "dataCollectorVersion": self.data_collector_version
        }


@dataclass
class DataType:
    name: str
    description: Optional[str]
    data_type:  Optional[str]
    unit: Optional[str]
    metadata: Optional[dict]

    @classmethod
    def from_odh_repr(cls, raw_data: dict):
        return cls(
            name=raw_data["tname"],
            description=raw_data.get("tdescription"),
            data_type=raw_data.get("ttype"),
            unit=raw_data.get("tunit"),
            metadata=raw_data.get("tmetadata")
        )

    def to_odh_repr(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "rtype": self.data_type,
            "unit": self.unit,
            "metadata": self.metadata,
            "_t": "it.bz.idm.bdp.dto.DataTypeDto"
        }


@dataclass
class Measure:
    station: Station
    data_type: DataType
    provenance: Provenance
    period: Optional[int]
    transaction_time: Optional[datetime]
    valid_time: datetime
    value: float or int or str

    @classmethod
    def from_odh_repr(cls, raw_data: dict):
        return cls(
            station=Station.from_odh_repr(raw_data),
            data_type=DataType.from_odh_repr(raw_data),
            provenance=Provenance.from_odh_repr(raw_data),
            period=raw_data.get("mperiod"),
            transaction_time=dateutil.parser.parse(raw_data["mtransactiontime"]) if raw_data.get("mtransactiontime") else None,
            valid_time=dateutil.parser.parse(raw_data["mvalidtime"]),
            value=raw_data["mvalue"],
        )

    def to_odh_repr(self) -> dict:
        return {
            "timestamp": self.valid_time.timestamp() * 1000,
            "value": self.value,
            "period": self.period,
            "_t": "it.bz.idm.bdp.dto.SimpleRecordDto"
        }


MeasureType = TypeVar("MeasureType", bound=Measure)


@dataclass
class Station:

    code: str
    active: bool
    available: bool
    coordinates: dict
    metadata: dict
    name: str
    station_type: str
    origin: Optional[str]

    @property
    def km(self) -> float:
        """
        Returns station mileage.
        """
        if self.metadata.get("a22_metadata"):
            metadata = ast.literal_eval(self.metadata["a22_metadata"])
            if metadata.get("metro"):
                return (int(metadata["metro"])) / 1000
        logger.warning(f"Mileage not defined for station [{self.code}]")
        return -1000

    __version__: ClassVar[int] = 1

    @classmethod
    def from_odh_repr(cls, raw_data: dict):
        return cls(
            code=raw_data["scode"],
            active=raw_data["sactive"],
            available=raw_data["savailable"],
            coordinates=raw_data["scoordinate"],
            metadata=raw_data["smetadata"],
            name=raw_data["sname"],
            station_type=raw_data["stype"],
            origin=raw_data.get("sorigin")
        )

    def to_json(self) -> dict:
        return {
            "code": self.code,
            "active": self.active,
            "available": self.available,
            "coordinates": self.coordinates,
            "metadata": self.metadata,
            "name": self.name,
            "station_type": self.station_type,
            "origin": self.origin
        }

    @classmethod
    def from_json(cls, dict_data) -> Station:
        return Station(
            code=dict_data["code"],
            active=dict_data["active"],
            available=dict_data["available"],
            coordinates=dict_data["coordinates"],
            metadata=dict_data["metadata"],
            name=dict_data["name"],
            station_type=dict_data["station_type"],
            origin=dict_data["origin"]
        )


StationType = TypeVar("StationType", bound=Station)


@dataclass
class MeasureCollection(Generic[MeasureType, StationType]):
    """
    This class represent a collection of measures and contains all the method necessary for filtering nad handling them.
    """

    measures: List[MeasureType] = field(default_factory=list)

    # apparently unused
    # def with_measure(self, measure: MeasureType) -> MeasureCollection:
    #     """
    #     Add a new traffic sensor to the collection
    #
    #     :param measure: the measure to add
    #     :return: the updated collection
    #     """
    #     self.measures.append(measure)
    #     return self
    #
    # def with_measures(self, measures: Iterable[MeasureType]) -> MeasureCollection:
    #     """
    #     Add a new traffic sensor to the collection
    #
    #     :param measures: the measures to add
    #     :return: the updated collection
    #     """
    #     self.measures.extend(measures)
    #     return self
    #
    # def get_measures_by_station(self, station: StationType) -> List[MeasureType]:
    #     """
    #     Filter the available measure by the given station
    #
    #     :param station: the station on which filter the measures
    #     :return: the measures filtered by the given station
    #     """
    #     return list(filter(lambda x: x.station == station, self.measures))

    def get_stations(self) -> Dict[str, StationType]:
        """
        Get the stations related to the measures in the format station_code: Station.

        :return: the stations related to the measures in the format station_code: Station.
        """
        stations_dict: Dict[str, StationType] = {}
        for measure in self.measures:
            if measure.station.code not in stations_dict:
                stations_dict[measure.station.code] = measure.station
        return stations_dict
