# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from datetime import datetime
from typing import List, Dict

from pandas import DataFrame

from common.data_model import TrafficSensorStation, VehicleClass
from common.data_model.history import HistoryMeasureCollection
from common.data_model.traffic import TrafficMeasureCollection
from common.data_model.validation import ValidationEntry, ValidationTypeClass
from common.model.helper import ModelHelper
from validator.Validator import validator

logger = logging.getLogger("pollution_v2.validator.model.validation_model")


class ValidationModel:
    """
    The model for computing validation data.
    """

    def compute_data(self, history: HistoryMeasureCollection, traffic: TrafficMeasureCollection,
                     station: TrafficSensorStation) -> List[ValidationEntry]:
        """
        Compute the validation given the available traffic measures

        :param history: A collection which contain measures history
        :param traffic: A collection which contain all the available traffic measures
        :param station: A station to be processed
        :return: A list of the new computed validation measures
        """

        history_dates = {measure.valid_time.date() for measure in history.measures}
        traffic_dates = {measure.valid_time.date() for measure in traffic.measures}

        if len(history_dates.difference(traffic_dates)) > 0:
            unprocessed_records = [measure.valid_time.date() for measure in traffic.measures
                                   if measure.valid_time.date() in history_dates.difference(traffic_dates)]
            logger.warning(f"Missing traffic data for the following dates [{history_dates.difference(traffic_dates)}] "
                           f"on station [{station.code}]: {len(unprocessed_records)} "
                           f"records will not be processed")
        if len(traffic_dates.difference(history_dates)) > 0:
            unprocessed_records = [measure.valid_time.date() for measure in traffic.measures
                                   if measure.valid_time.date() in traffic_dates.difference(history_dates)]
            logger.warning(f"Missing history data for the following dates [{traffic_dates.difference(history_dates)}] "
                           f"on station [{station.code}]: {len(unprocessed_records)} "
                           f"records will not be processed")

        run_on_dates = history_dates.intersection(traffic_dates)
        logger.info(f"Ready to process validation on the following dates [{run_on_dates}]")

        traffic_entries = traffic.get_entries()
        history_entries = history.get_entries()

        stations_df = ModelHelper.get_stations_dataframe(traffic.get_stations())
        stations_df_validator = stations_df.copy().set_index("station_id")

        # TODO coming from algorithm?
        period = 600

        res = []
        if len(traffic_entries) > 0 and len(history_entries) > 0:
            for date in run_on_dates:
                traffic_df = ModelHelper.get_traffic_dataframe_for_validation(traffic_entries, date)
                logger.info(f"Startig validation on {len(traffic_df)} traffic records on station [{station.code}]")
                history_df = ModelHelper.get_history_dataframe(history_entries, date)
                out_df = validator(date.strftime('%Y-%m-%d'), traffic_df, history_df,
                                   stations_df_validator[['km']], stations_df_validator[['station_type']])
                lst = self._get_entries_from_df(out_df, date.strftime('%Y-%m-%d'), period, traffic.get_stations())
                res.extend(lst)
        else:
            logger.info("0 validated entries found skipping pollution computation")
            return []

        return res

    @staticmethod
    def _get_entries_from_df(in_df: DataFrame, date: str, period: int,
                             stations_dict: Dict[str, TrafficSensorStation]) -> List[ValidationEntry]:
        """
        Create a list of entries for the given dataframe.

        :param in_df: the dataframe
        :param stations_dict: the stations related to the measures in the format station_code: Station
        :return: the list of entries
        """
        out_entries = []
        for _, row in in_df.iterrows():
            out_entries.append(ValidationEntry(
                station=stations_dict[row['station_code']],
                valid_time=datetime.fromisoformat(f"{date}T{row['time']}"),
                vehicle_class=VehicleClass(row["variable"]),
                entry_class=ValidationTypeClass.VALID,
                entry_value=row["is_valid"],
                period=period
            ))
        return out_entries
