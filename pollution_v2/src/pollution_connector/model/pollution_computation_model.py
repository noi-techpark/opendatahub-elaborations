# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import datetime
import json
import logging
from typing import List, Iterable, Dict

import pandas as pd

from common.data_model.common import VehicleClass
from common.data_model.pollution import PollutionEntry, PollutantClass
from common.data_model import TrafficMeasureCollection, TrafficEntry, TrafficSensorStation
from common.model.helper import ModelHelper
from pollution_connector.model.CopertEmissions import copert_emissions

logger = logging.getLogger("pollution_v2.pollution_connector.model.pollution_computation_model")


class PollutionComputationModel:
    """
    The model for computing pollution data.
    """

    @staticmethod
    def _get_pollution_entries_from_df(pollution_df: pd.DataFrame, stations_dict: Dict[str, TrafficSensorStation]) -> List[PollutionEntry]:
        """
        Create a list of PollutionEntry for the given dataframe. The dataframe should have the following columns:
        date,time,Location,Station,Lane,Category,km,Pollutant,Total_Transits,E

        :param pollution_df: the pollution dataframe
        :param stations_dict: the stations related to the measures in the format station_code: Station
        :return: the list of pollution entries
        """
        pollution_entries = []
        for _, row in pollution_df.iterrows():
            pollution_entries.append(PollutionEntry(
                station=stations_dict[f"{row['Location']}:{row['Station']}:{row['Lane']}"],
                valid_time=datetime.datetime.fromisoformat(f"{row['date']}T{row['time']}"),
                vehicle_class=VehicleClass(row["Category"]),
                entry_class=PollutantClass(row["Pollutant"]),
                entry_value=row["E"],
                period=row["Period"]
            ))
        return pollution_entries

    # TODO should become ValidationMeasureCollection
    def compute_data(self, validated_measure_collection: TrafficMeasureCollection) -> List[PollutionEntry]:
        """
        Compute the pollution measure given the available traffic measures
        :param validated_measure_collection: A collection which contain all the available and validated traffic measures
        :return: A list of the new computed pollution measures
        """
        validated_entries = validated_measure_collection.get_entries()

        if len(validated_entries) > 0:
            validated_df = ModelHelper.get_traffic_dataframe(validated_entries)
            pollution_df = copert_emissions(validated_df)
            return self._get_pollution_entries_from_df(pollution_df, validated_measure_collection.get_stations())
        else:
            logger.info("0 validated entries found skipping pollution computation")
            return []
