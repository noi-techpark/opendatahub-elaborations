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
from common.data_model.validation import ValidationMeasureCollection
from common.model.helper import ModelHelper
from pollution_connector.model.CopertEmissions import copert_emissions

logger = logging.getLogger("pollution_v2.pollution_connector.model.pollution_computation_model")


class PollutionComputationModel:
    """
    The model for computing pollution data.
    """

    @staticmethod
    def _get_pollution_entries_from_df(pollution_df: pd.DataFrame, stations_dict: Dict[str, TrafficSensorStation]) -> \
        List[PollutionEntry]:
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

    def compute_data(self, validation: ValidationMeasureCollection,
                     traffic: TrafficMeasureCollection, station: TrafficSensorStation) -> List[PollutionEntry]:
        """
        Compute the pollution measure given the available traffic measures
        :param validation: A collection which contain all the available and validated traffic measures
        :param traffic: A collection which contain all the available traffic measures
        :param station: A station to be processed
        :return: A list of the new computed pollution measures
        """

        validation_data_types = {str(measure.data_type) for measure in validation.measures}
        traffic_data_types = {str(measure.data_type) for measure in traffic.measures}

        logger.info(f"{len(validation.measures)} validation measures available "
                    f"on {len(validation_data_types)} data types")
        valid_measures = [measure for measure in validation.measures if measure.value == 1]
        logger.info(f"{len(valid_measures)} "
                    f"validation measures available computed as valid "
                    f"on {len(validation_data_types)} data types")
        logger.info(f"{len(traffic.measures)} traffic measures available "
                    f"on {len(traffic_data_types)} data types")

        validated_datetimes = {measure.valid_time for measure in valid_measures}
        traffic_datetimes = {measure.valid_time for measure in traffic.measures}

        diff_datetime = {measure.valid_time.strftime("%m/%d/%Y, %H:%M:%S") for measure in traffic.measures
                         if measure.valid_time in traffic_datetimes.difference(validated_datetimes)}
        diff_date = {measure.valid_time.strftime("%m/%d/%Y") for measure in traffic.measures
                     if measure.valid_time in traffic_datetimes.difference(validated_datetimes)}
        if len(diff_datetime) > 0:
            logger.warning(
                f"{len(diff_datetime)} discarded records: no validation "
                f"for the dates [{sorted(diff_date)}] on station [{station.code}]) "
                f"(and datetimes [{sorted(diff_datetime)}]")

        run_on_datetimes = validated_datetimes.intersection(traffic_datetimes)
        logger.info(f"Ready to process pollution computation on {len(run_on_datetimes)} datetimes")

        traffic_entries = traffic.get_entries()

        if len(traffic_entries) > 0:
            traffic_df = ModelHelper.get_traffic_dataframe(traffic_entries, run_on_datetimes)
            pollution_df = copert_emissions(traffic_df)
            return self._get_pollution_entries_from_df(pollution_df, traffic.get_stations())
        else:
            logger.info("0 validated entries found skipping pollution computation")
            return []
