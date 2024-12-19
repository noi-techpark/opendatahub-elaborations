# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import ast
from dataclasses import dataclass

import logging
from typing import Optional, ClassVar, TypeVar

logger = logging.getLogger("pollution_v2.common.data_model.station")


@dataclass
class Station:

    code: str
    wrf_code: Optional[str]
    meteo_station_code: Optional[str]
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
        logger.debug(f"Mileage not defined for station [{self.code}]")
        return -1000

    @property
    def sensor_type(self) -> float:
        """
        Returns sensor type.
        """
        return self.metadata.get("sensor_type")

    __version__: ClassVar[int] = 1

    def to_odh_repr(self) -> dict:
        return {
            "scode": self.code,
            # TODO: check if need to add `wrf_code` and `meteo_station_code` to the ODH representation
            "sactive": self.active,
            "savailable": self.available,
            "scoordinate": self.coordinates,
            "smetadata": self.metadata,
            "sname": self.name,
            "stype": self.station_type,
            "sorigin": self.origin
        }

    @classmethod
    def from_odh_repr(cls, raw_data: dict):
        return cls(
            code=raw_data["scode"],
            wrf_code=raw_data.get("wrf_code", None),  # TODO: is this field ever saved in ODH?
            meteo_station_code=raw_data.get("meteo_station_code", None),  # TODO: is this field ever saved in ODH?
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
            "wrf_code": self.wrf_code,
            "meteo_station_code": self.meteo_station_code,
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
        res = Station(
            code=dict_data["code"],
            wrf_code=dict_data.get("wrf_code", None),
            meteo_station_code=dict_data.get("meteo_station_code", None),
            active=dict_data["active"],
            available=dict_data["available"],
            coordinates=dict_data["coordinates"],
            metadata=dict_data["metadata"],
            name=dict_data["name"],
            station_type=dict_data["station_type"],
            origin=dict_data["origin"]
        )
        return res


StationType = TypeVar("StationType", bound=Station)


@dataclass
class TrafficSensorStation(Station):
    """
    Class representing a traffic station.
    """

    @staticmethod
    def split_station_code(code: str) -> (str, int, int):
        """
        splits the station code using the pattern ID_strada:ID_stazione:ID_corsia and returns a tuple
        with the following structure (ID_strada, ID_stazione, ID_corsia)
        :return:
        """
        splits = code.split(":")
        if len(splits) != 3:
            raise ValueError(f"Unable to split [{code}] in ID_strada:ID_stazione:ID_corsia")
        return splits[0], int(splits[1]), int(splits[2])

    @property
    def id_strada(self) -> str:
        id_strada, id_stazione, id_corsia = self.split_station_code(self.code)
        return id_strada

    @property
    def id_stazione(self) -> int:
        id_strada, id_stazione, id_corsia = self.split_station_code(self.code)
        return id_stazione

    @property
    def id_corsia(self) -> int:
        id_strada, id_stazione, id_corsia = self.split_station_code(self.code)
        return id_corsia

    @classmethod
    def from_json(cls, dict_data) -> TrafficSensorStation:
        wrf_code = dict_data.get("wrf_code") if dict_data.get("wrf_code") is not None else None
        meteo_station_code = dict_data.get("meteo_station_code") if dict_data.get("meteo_station_code") is not None else None
        return TrafficSensorStation(
            code=dict_data["code"],
            active=dict_data["active"],
            available=dict_data["available"],
            coordinates=dict_data["coordinates"],
            metadata=dict_data["metadata"],
            name=dict_data["name"],
            station_type=dict_data["station_type"],
            origin=dict_data["origin"],
            wrf_code=wrf_code,
            meteo_station_code=meteo_station_code
        )
