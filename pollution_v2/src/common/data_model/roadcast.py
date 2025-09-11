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

    RW_FORECAST_CONF_LEVEL = 'forecast-conf_level'

    RW_FORECAST_60 = 'forecast-60'
    RW_FORECAST_120 = 'forecast-120'
    RW_FORECAST_180 = 'forecast-180'
    RW_FORECAST_240 = 'forecast-240'
    RW_FORECAST_300 = 'forecast-300'
    RW_FORECAST_360 = 'forecast-360'
    RW_FORECAST_420 = 'forecast-420'
    RW_FORECAST_480 = 'forecast-480'
    RW_FORECAST_540 = 'forecast-540'
    RW_FORECAST_600 = 'forecast-600'
    RW_FORECAST_660 = 'forecast-660'
    RW_FORECAST_720 = 'forecast-720'
    RW_FORECAST_780 = 'forecast-780'
    RW_FORECAST_840 = 'forecast-840'
    RW_FORECAST_900 = 'forecast-900'
    RW_FORECAST_960 = 'forecast-960'
    RW_FORECAST_1020 = 'forecast-1020'
    RW_FORECAST_1080 = 'forecast-1080'
    RW_FORECAST_1140 = 'forecast-1140'
    RW_FORECAST_1200 = 'forecast-1200'
    RW_FORECAST_1260 = 'forecast-1260'
    RW_FORECAST_1320 = 'forecast-1320'
    RW_FORECAST_1380 = 'forecast-1380'
    RW_FORECAST_1440 = 'forecast-1440'
    RW_FORECAST_1500 = 'forecast-1500'
    RW_FORECAST_1560 = 'forecast-1560'
    RW_FORECAST_1620 = 'forecast-1620'
    RW_FORECAST_1680 = 'forecast-1680'
    RW_FORECAST_1740 = 'forecast-1740'
    RW_FORECAST_1800 = 'forecast-1800'
    RW_FORECAST_1860 = 'forecast-1860'
    RW_FORECAST_1920 = 'forecast-1920'
    RW_FORECAST_1980 = 'forecast-1980'
    RW_FORECAST_2040 = 'forecast-2040'
    RW_FORECAST_2100 = 'forecast-2100'
    RW_FORECAST_2160 = 'forecast-2160'
    RW_FORECAST_2220 = 'forecast-2220'
    RW_FORECAST_2280 = 'forecast-2280'
    RW_FORECAST_2340 = 'forecast-2340'
    RW_FORECAST_2400 = 'forecast-2400'
    RW_FORECAST_2460 = 'forecast-2460'
    RW_FORECAST_2520 = 'forecast-2520'
    RW_FORECAST_2580 = 'forecast-2580'
    RW_FORECAST_2640 = 'forecast-2640'
    RW_FORECAST_2700 = 'forecast-2700'
    RW_FORECAST_2760 = 'forecast-2760'
    RW_FORECAST_2820 = 'forecast-2820'
    RW_FORECAST_2880 = 'forecast-2880'

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
        return (
            f"station: {self.station.code}, valid_time: {self.valid_time}, roadcast_class: {self.roadcast_class.name}, "
            f"entry_class: {self.entry_class}, entry_value: {self.entry_value}, period: {self.period}")


@dataclass
class ExtendedRoadCastEntry(RoadCastEntry):
    conf_level = None

    def __init__(self, station: Station, valid_time: datetime, roadcast_class: RoadCastClass,
                 entry_class: RoadCastTypeClass, entry_value: Optional[float], period: Optional[int]):
        super().__init__(station, valid_time, roadcast_class, entry_class, entry_value, period)

    def set_conf_level(self, value):
        self.conf_level = value

    def __str__(self):
        return (
            f"station: {self.station.code}, valid_time: {self.valid_time}, roadcast_class: {self.roadcast_class.name}, "
            f"entry_class: {self.entry_class}, entry_value: {self.entry_value}, period: {self.period}, "
            f"conf_level: {self.conf_level}")


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
