# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from enum import Enum

from dataclasses import dataclass
from datetime import datetime
import dateutil.parser
from typing import Optional, List

from common.data_model.common import MeasureCollection, Measure, DataType, Provenance
from common.data_model.entry import GenericEntry
from common.data_model.station import Station


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


class PollutionDispersalMeasure(Measure):
    """
    Measure representing pollution dispersal measure.
    """

    def __init__(self, x_coordinate: float, y_coordinate: float, z_coordinate: float, **kwargs):
        super().__init__(**kwargs)
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.z_coordinate = z_coordinate

    # TODO: implement get_data_types method
    @staticmethod
    def get_data_types() -> List[DataType]:
        # TODO: or implement the coordinates as a datatype?
        pass

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
    Collection of pollution dispersal measure measures.
    """
    pass
    # def get_entries(self) -> List[PollutionDispersalEntry]:
    #     """
    #     Build and retrieve the list of traffic entry from the available measures
    #
    #     :return: a list of traffic entries
    #     """
    #     return list(self._get_entries_iterator())
    #
    # def _get_entries_iterator(self) -> Iterator[PollutionDispersalEntry]:
    #     """
    #     Build and retrieve the iterator for list of observation entries from the available measures
    #
    #     :return: an iterator of traffic entries
    #     """
    #     for station_dict in self._build_entries_dictionary().values():
    #         for entry in station_dict.values():
    #             yield entry
    #
    # def _build_entries_dictionary(self) -> Dict[str, Dict[datetime, PollutionDispersalEntry]]:
    #     # A temporary dictionary used for faster aggregation of the results
    #     # The dictionary will have the following structure
    #     # StationCode -> (measure valid time -> (PollutionDispersalEntry))
    #     tmp: Dict[str, Dict[datetime, dict]] = {}
    #     stations: Dict[str, Station] = {}
    #     for measure in self.measures:
    #         if measure.station.code not in stations:
    #             stations[measure.station.code] = measure.station
    #         if measure.station.code not in tmp:
    #             tmp[measure.station.code] = {}
    #         if measure.valid_time not in tmp[measure.station.code]:
    #             tmp[measure.station.code][measure.valid_time] = {}
    #         tmp[measure.station.code][measure.valid_time][measure.data_type.name] = measure.value
    #
    #     result: Dict[str, Dict[datetime, PollutionDispersalEntry]] = {}
    #     for group_by_station in tmp:
    #         if group_by_station not in result:
    #             result[group_by_station] = {}
    #         for group_by_time in tmp[group_by_station]:
    #             entry = tmp[group_by_station][group_by_time]
    #             result[group_by_station][group_by_time] = PollutionDispersalEntry(
    #                 station=stations[group_by_station],
    #                 valid_time=group_by_time,
    #                 period=1,
    #                 x_coordinate=entry[PollutionDispersalMeasureType.X_COORDINATE],
    #                 y_coordinate=entry[PollutionDispersalMeasureType.Y_COORDINATE],
    #                 z_coordinate=entry[PollutionDispersalMeasureType.Z_COORDINATE],
    #                 c_a22=entry[PollutionDispersalMeasureType.C_A22],
    #             )
    #
    #     return result
