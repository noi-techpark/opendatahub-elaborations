# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Iterator, List

import dateutil.parser

from common.data_model.common import Measure, MeasureCollection, DataType, Provenance
from common.data_model.entry import GenericEntry
from common.data_model.station import TrafficSensorStation


class HistoryMeasureType(Enum):

    NR_VEHICLES = "Nr. Vehicles"


@dataclass
class HistoryMeasure(Measure):
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


@dataclass
class HistoryEntry(GenericEntry):

    def __init__(self, station: TrafficSensorStation, valid_time: datetime, nr_of_vehicles: int, period: Optional[int]):
        super().__init__(station, valid_time, period)
        self.nr_of_vehicles = nr_of_vehicles


@dataclass
class HistoryMeasureCollection(MeasureCollection[HistoryMeasure, TrafficSensorStation]):

    def _build_entries_iterator(self) -> Iterator[HistoryEntry]:
        # A temporary dictionary used for faster aggregation of the results
        # The dictionary will have the following structure
        # StationCode -> (measure valid time -> (vehicle class -> TrafficEntry))
        result: Dict[str, Dict[datetime, HistoryEntry]] = {}
        for measure in self.measures:
            if measure.station.code not in result:
                result[measure.station.code] = {}
            if measure.valid_time not in result[measure.station.code]:
                entry = HistoryEntry(
                    station=measure.station,
                    valid_time=measure.valid_time,
                    nr_of_vehicles=measure.value,
                    period=measure.period
                )
                result[measure.station.code][measure.valid_time] = entry

        for station_dict in result.values():
            for entry in station_dict.values():
                yield entry

    def get_entries(self) -> List[HistoryEntry]:
        """
        Build and retrieve the list of entries from the available measures

        :return: a list of entries
        """
        return list(self._build_entries_iterator())
