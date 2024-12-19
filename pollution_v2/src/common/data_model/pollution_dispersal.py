# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from common.data_model.common import MeasureCollection, Measure, DataType, Provenance
from common.data_model.entry import GenericEntry
from common.data_model.station import Station
from common.settings import DATATYPE_PREFIX


@dataclass
class PollutionDispersalEntry(GenericEntry):

    def __init__(self, station: Station, valid_time: datetime, concentration_value: float, period: Optional[int]):
        super().__init__(station, valid_time, period)
        self.concentration_value = concentration_value

    def __repr__(self):
        return (f"PollutionDispersalEntry(station={self.station}, valid_time={self.valid_time}, "
                f"concentration_value={self.concentration_value}, period={self.period})")


class PollutionDispersalMeasure(Measure):
    """
    Measure representing pollution dispersal measure.
    """

    @staticmethod
    def get_data_types() -> List[DataType]:
        # TODO: is it correct?
        return [DataType(
            name=f"{DATATYPE_PREFIX}concentration",
            description="Pollution dispersal concentration",
            data_type="Dispersal",
            unit="ug/m3",
            metadata={}
        )]


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
        dispersal_measures: List[PollutionDispersalMeasure] = []
        data_type = PollutionDispersalMeasure.get_data_types()[0]
        for entry in entries:
            dispersal_measures.append(PollutionDispersalMeasure(
                station=entry.station,
                data_type=data_type,
                provenance=provenance,
                period=entry.period,
                transaction_time=None,  # TODO: check
                valid_time=entry.valid_time,
                value=entry.concentration_value,
            ))

        return PollutionDispersalMeasureCollection(dispersal_measures)
