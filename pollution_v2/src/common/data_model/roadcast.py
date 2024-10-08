# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict

from common.data_model import Station
from common.data_model.common import MeasureCollection, Measure, Provenance, DataType
from common.data_model.entry import GenericEntry
from common.settings import DATATYPE_PREFIX


class RoadCastClass(Enum):

    ROADCAST = "ROADCAST"


class RoadCastTypeClass(Enum):
    """
    not defined as enum and used to define all values as they are dinamically determined at runtime
    on the basis of the number of forecasts requested
    """

    RW_FORECAST_60 = "forecast-60"
    RW_FORECAST_120 = "forecast-120"
    RW_FORECAST_180 = "forecast-180"
    RW_FORECAST_240 = "forecast-240"

    @classmethod
    def get_by_suffix(cls, suffix: str):
        try:
            return RoadCastTypeClass(f"forecast-{suffix}")
        except ValueError:
            return None


@dataclass
class RoadCastEntry(GenericEntry):

    def __init__(self, station: Station, valid_time: datetime, roadcast_class: RoadCastClass,
                 entry_class: RoadCastTypeClass, entry_value: Optional[float], period: Optional[int]):
        super().__init__(station, valid_time, period)
        self.entry_class = entry_class
        self.roadcast_class = roadcast_class
        self.entry_value = entry_value

    def __str__(self):
        return (f"station: {self.station.code}, valid_time: {self.valid_time}, roadcast_class: {self.roadcast_class.name}, "
                f"entry_class: {self.entry_class}, entry_value: {self.entry_value}, period: {self.period}")


class RoadCastMeasure(Measure):
    """
    Measure representing roadcast.
    """

    @staticmethod
    def get_data_types() -> List[DataType]:
        """
        Returns the data types specific for this measure.

        :return: the data types specific for this measure
        """
        data_types = []
        for roadcast in RoadCastClass:
            for roadcast_type in RoadCastTypeClass:
                data_types.append(
                    DataType(f"{DATATYPE_PREFIX}{roadcast.name}-{roadcast_type.name}",
                             f"{roadcast.value} for {roadcast_type.value}", "Roadcast", "-", {}))
        return data_types


@dataclass
class RoadCastMeasureCollection(MeasureCollection[RoadCastMeasure, Station]):

    @staticmethod
    def build_from_entries(roadcast_entries: List[RoadCastEntry],
                           provenance: Provenance, filter_is_valid=False) -> RoadCastMeasureCollection:
        """
        Build a RoadCastMeasureCollection from the list of roadcast entries.

        :param roadcast_entries: the roadcast entries from which generate the RoadCastMeasureCollection
        :param provenance: the provenance of the validation measures
        :param filter_is_valid: if True, processes only the measure with is_valid set to True TODO tenere?
        :return: a RoadCastMeasureCollection object containing the roadcast measures generated from the roadcast entries
        """
        data_types_dict: Dict[str, DataType] = {data_type.name: data_type for data_type in
                                                RoadCastMeasure.get_data_types()}

        roadcast_measures: List[RoadCastMeasure] = []
        for roadcast_entry in roadcast_entries:
            if not filter_is_valid or (filter_is_valid and roadcast_entry.entry_value == 1):
                roadcast_measures.append(RoadCastMeasure(
                    station=roadcast_entry.station,
                    data_type=data_types_dict[
                        f"{DATATYPE_PREFIX}{roadcast_entry.roadcast_class.name}-{roadcast_entry.entry_class.name}"],
                    provenance=provenance,
                    period=roadcast_entry.period,
                    transaction_time=None,
                    valid_time=roadcast_entry.valid_time,
                    value=roadcast_entry.entry_value
                ))

        return RoadCastMeasureCollection(roadcast_measures)
