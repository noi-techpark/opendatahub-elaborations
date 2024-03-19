# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Iterator

import dateutil.parser

from common.data_model import TrafficSensorStation
from common.data_model.common import Measure, MeasureCollection, DataType, Provenance




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
class HistoryEntry:
    station: TrafficSensorStation
    transaction_time: datetime
    valid_time: datetime
    nr_of_vehicles: int
    period: Optional[int]


@dataclass
class HistoryMeasureCollection(MeasureCollection[HistoryMeasure, TrafficSensorStation]):

    def _build_history_entries_dictionary(self) -> Dict[str, Dict[datetime, HistoryEntry]]:
        # A temporary dictionary used for faster aggregation of the results
        # The dictionary will have the following structure
        # StationCode -> (measure valid time -> (vehicle class -> TrafficEntry))
        result: Dict[str, Dict[datetime, HistoryEntry]] = {}
        for measure in self.measures:
            if measure.station.code not in result:
                result[measure.station.code] = {}
            elif measure.valid_time in result[measure.station.code]:
                entry = HistoryEntry(
                    station=measure.station,
                    transaction_time=measure.transaction_time,
                    valid_time=measure.valid_time,
                    nr_of_vehicles=measure.value,
                    period=measure.period
                )
                result[measure.station.code][measure.valid_time] = entry

        return result

    def get_history_entries(self) -> Iterator[HistoryEntry]:
        """
        Build and retrieve the list of entry from the available measures

        :return: an iterator of entries
        """
        for station_dict in self._build_history_entries_dictionary().values():
            for date_dict in station_dict.values():
                for entry in date_dict.values():
                    yield entry
