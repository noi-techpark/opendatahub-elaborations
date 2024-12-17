# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from enum import Enum

from dataclasses import dataclass
from datetime import datetime
import dateutil.parser
from typing import Optional, List, Dict

from common.data_model.common import MeasureCollection, Measure, DataType, Provenance
from common.data_model.entry import GenericEntry
from common.data_model.station import Station
from common.settings import DATATYPE_PREFIX


class PollutionDispersalMeasureType(Enum):

    X_COORDINATE = 'X-Coordinate'
    Y_COORDINATE = 'Y-Coordinate'
    Z_COORDINATE = 'Z-Coordinate'
    C_A22 = 'C_A22'


@dataclass
class PollutionDispersalEntry(GenericEntry):

    def __init__(self, station: Station, valid_time: datetime, x_coordinate: float, y_coordinate: float,
                 z_coordinate: float, c_a22: float, period: Optional[int]):
        super().__init__(station, valid_time, period)
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.z_coordinate = z_coordinate
        self.c_a22 = c_a22

    def __repr__(self):
        return (f"PollutionDispersalEntry(station={self.station}, valid_time={self.valid_time}, "
                f"x_coordinate={self.x_coordinate}, y_coordinate={self.y_coordinate}, "
                f"z_coordinate={self.z_coordinate}, c_a22={self.c_a22}, period={self.period})")


class PollutionDispersalMeasure(Measure):
    """
    Measure representing pollution dispersal measure.
    """

    def __init__(self, x_coordinate: float, y_coordinate: float, z_coordinate: float, **kwargs):
        super().__init__(**kwargs)
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.z_coordinate = z_coordinate

    @staticmethod
    def get_data_types() -> List[DataType]:
        # TODO: or implement the coordinates as a datatype?
        return [DataType(
            name=f"{DATATYPE_PREFIX}NOx-pollution-dispersal",
            description="NOx pollution dispersal",
            data_type="Dispersal",
            unit="-",
            metadata={}
        )]

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
            x_coordinate=raw_data["x_coordinate"],
            y_coordinate=raw_data["y_coordinate"],
            z_coordinate=raw_data["z_coordinate"],
        )

    def to_odh_repr(self) -> dict:
        repr = super().to_odh_repr()
        repr.update({
            "x_coordinate": self.x_coordinate,
            "y_coordinate": self.y_coordinate,
            "z_coordinate": self.z_coordinate,
        })
        return repr


@dataclass
class PollutionDispersalMeasureCollection(MeasureCollection[PollutionDispersalMeasure, Station]):
    """
    Collection of pollution dispersal measures.
    """

    @staticmethod
    def build_from_entries(entries: List[PollutionDispersalEntry],
                           provenance: Provenance) -> PollutionDispersalMeasureCollection:
        """
        Build a PollutionDispersalMeasureCollection from the list of pollution dispersal entries.

        :param entries: the pollution dispersal entries from which generate the PollutionDispersalMeasureCollection
        :param provenance: the provenance of the pollution dispersal measures
        :return: a PollutionDispersalMeasureCollection object containing the pollution dispersal measures generated from the respective entries
        """
        pollution_measures: List[PollutionDispersalMeasure] = []
        data_type = PollutionDispersalMeasure.get_data_types()[0]
        for entry in entries:
            pollution_measures.append(PollutionDispersalMeasure(
                station=entry.station,
                data_type=data_type,
                provenance=provenance,
                period=entry.period,
                transaction_time=None,
                valid_time=entry.valid_time,
                # TODO: is this the correct implementation to push the coordinates?
                #       alternatively, should the coordinates be set in the data_types?
                #       (Although they can't be known beforehand and can only be retrieved for a station using '*')
                value=entry.c_a22,
                x_coordinate=entry.x_coordinate,
                y_coordinate=entry.y_coordinate,
                z_coordinate=entry.z_coordinate,
            ))

        return PollutionDispersalMeasureCollection(pollution_measures)
