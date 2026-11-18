# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import datetime
import logging
from typing import List, Dict

import pandas as pd

from common.data_model.common import VehicleClass
from common.data_model.pollution import PollutionEntry, PollutantClass
from common.data_model import TrafficMeasureCollection, TrafficSensorStation
from common.model.helper import ModelHelper
from pollution_computer.model.CopertEmissions import copert_emissions

logger = logging.getLogger("pollution_v2.pollution_computer.model.pollution_computation_model")


class PollutionComputationModel:
    """
    The model for computing pollution data.
    """

    @staticmethod
    def _get_pollution_entries_from_df(pollution_df: pd.DataFrame,
                                       stations_dict: Dict[str, TrafficSensorStation]) -> List[PollutionEntry]:
        pollution_entries = []
        known_pollutants = {p.value for p in PollutantClass}
        pollution_df = pollution_df[pollution_df["Pollutant"].isin(known_pollutants)]
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

    def compute_data(self, traffic: TrafficMeasureCollection, station: TrafficSensorStation) -> List[PollutionEntry]:
        traffic_data_types = {str(measure.data_type) for measure in traffic.measures}
        run_on_datetimes = {measure.valid_time for measure in traffic.measures}

        logger.info(f"{len(traffic.measures)} traffic measures on {len(traffic_data_types)} data types")
        logger.info(f"Ready to process pollution computation on {len(run_on_datetimes)} datetimes")

        traffic_entries = traffic.get_entries()
        if run_on_datetimes and traffic_entries:
            traffic_df = ModelHelper.get_traffic_dataframe(traffic_entries, run_on_datetimes)
            try:
                year = sorted({date.strftime("%Y") for date in run_on_datetimes})[-1]
            except Exception:
                year = ""
            pollution_df = copert_emissions(traffic_df, year)
            return self._get_pollution_entries_from_df(pollution_df, traffic.get_stations())

        logger.info("0 traffic entries found, skipping pollution computation")
        return []
