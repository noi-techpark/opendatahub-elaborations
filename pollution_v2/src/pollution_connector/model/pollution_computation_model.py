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
from common.model.model import GenericModel
from pollution_connector.model.CopertEmissions import copert_emissions

logger = logging.getLogger("pollution_connector.model.pollution_computation_model")


class PollutionComputationModel(GenericModel):

    def __init__(self):
        pass

    def _compute(self, traffic_df: pd.DataFrame) -> pd.DataFrame:
        emissions_df = copert_emissions(traffic_df)
        return emissions_df

    @staticmethod
    def _get_traffic_dataframe(traffic_entries: Iterable[TrafficEntry]) -> pd.DataFrame:
        """
        Get a dataframe from the given traffic entries. The resulting dataframe will have the following columns:
        date,time,Location,Station,Lane,Category,Transits,Speed,km

        :param traffic_entries: the traffic entries
        :return: the traffic dataframe
        """
        temp = []
        for entry in traffic_entries:

            km = None
            if "a22_metadata" in entry.station.metadata:
                try:
                    meta: dict = json.loads(entry.station.metadata["a22_metadata"])
                    km = meta.get("metro")
                except Exception as e:
                    logger.warning(f"Unable to parse the KM data for station [{entry.station.code}], error [{e}]")

            temp.append({
                "date": entry.valid_time.date().isoformat(),
                "time": entry.valid_time.time().isoformat(),
                "Location": entry.station.id_strada,
                "Station": entry.station.id_stazione,
                "Lane": entry.station.id_corsia,
                "Category": entry.vehicle_class.value,
                "Transits": entry.nr_of_vehicles,
                "Speed": entry.average_speed,
                "Period": entry.period,
                "KM": km
            })

        return pd.DataFrame(temp)

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

    def compute_data(self, traffic_measure_collection: TrafficMeasureCollection) -> List[PollutionEntry]:
        """
        Compute the pollution measure given the available traffic measures
        :param traffic_measure_collection: A collection which contain all the available traffic measures
        :return: A list of the new computed pollution measures
        """
        traffic_entries = list(traffic_measure_collection.get_traffic_entries())

        if len(traffic_entries) > 0:
            traffic_df = self._get_traffic_dataframe(traffic_entries)
            pollution_df = self._compute(traffic_df)
            return self._get_pollution_entries_from_df(pollution_df, traffic_measure_collection.get_stations())
        else:
            logger.info("0 traffic entries found skipping pollution computation")
            return []
