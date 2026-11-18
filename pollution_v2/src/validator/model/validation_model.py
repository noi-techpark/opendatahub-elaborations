# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from datetime import datetime, timedelta
from typing import List, Dict

from pandas import DataFrame

from common.data_model import TrafficSensorStation, VehicleClass
from common.data_model.history import HistoryMeasureCollection
from common.data_model.traffic import TrafficMeasureCollection
from common.data_model.validation import ValidationEntry, ValidationTypeClass
from common.model.helper import ModelHelper
from common.settings import HISTORY_TIMEZONE, PERIOD_1DAY
from validator.Validator import validator

logger = logging.getLogger("pollution_v2.validator.model.validation_model")


def _get_station_on_logs(stations: List[TrafficSensorStation]):
    return (f"[{', '.join([station.code for station in (stations[:5] if len(stations) > 5 else stations)])}"
            f"{' and more (' + str(len(stations)) + ')' if len(stations) > 5 else ''}]")


class ValidationModel:
    """
    The model for computing validation data.
    """

    def compute_data(self, history: HistoryMeasureCollection, traffic: TrafficMeasureCollection,
                     stations: List[TrafficSensorStation]) -> List[ValidationEntry]:
        """
        Compute the validation given the available traffic measures

        :param history: A collection which contain measures history
        :param traffic: A collection which contain all the available traffic measures
        :param stations: List of all stations
        :return: A list of the new computed validation measures
        """

        # since the daily history dates are inserted at start of next day, consider them for the day before
        history_dates = {(measure.valid_time-timedelta(days=1)).date() for measure in history.measures}
        traffic_dates = {measure.valid_time.date() for measure in traffic.measures}
        
        logger.debug(f"Considering total of {len(history_dates)} history and {len(traffic_dates)} traffic dates")

        traffic_missing_dates = history_dates.difference(traffic_dates)
        if len(traffic_missing_dates) > 0:
            logger.warning(f"Missing traffic data for the following dates [{sorted(traffic_missing_dates)}] "
                           f"while processing [{_get_station_on_logs(stations)}]: {len(traffic_missing_dates)} "
                           f"records will not be processed")
        history_missing_dates = traffic_dates.difference(history_dates)
        if len(history_missing_dates) > 0:
            logger.warning(f"Missing history data for the following dates [{sorted(history_missing_dates)}] "
                           f"while processing [{_get_station_on_logs(stations)}]: {len(history_missing_dates)} "
                           f"records will not be processed")

        run_on_dates = history_dates.intersection(traffic_dates)
        logger.debug(f"Ready to process validation on the following dates [{sorted(run_on_dates)}]")

        traffic_entries = traffic.get_entries()
        history_entries = history.get_entries()

        stations_df = ModelHelper.get_stations_dataframe(stations)

        res = []
        if len(traffic_entries) > 0 and len(history_entries) > 0:
            for date in run_on_dates:
                traffic_df = ModelHelper.get_traffic_dataframe_for_validation(traffic_entries, date)
                logger.debug(f"Starting validation on {len(traffic_df)} traffic records on station "
                             f"[{_get_station_on_logs(stations)}] on [{date.isoformat()}]")
                history_df = ModelHelper.get_history_dataframe(history_entries, date)
                out_df = validator(date.strftime('%Y-%m-%d'), traffic_df, history_df,
                                   stations_df[["station_id", "km"]].drop_duplicates().set_index("station_id")["km"].to_dict(),
                                   stations_df[["station_id", "station_type"]].drop_duplicates().set_index("station_id")["station_type"].to_dict())
                lst = self._get_entries_from_df(out_df, date.strftime('%Y-%m-%d'), PERIOD_1DAY, traffic.get_stations())
                res.extend(lst)
        else:
            logger.warning("0 validated entries found skipping pollution computation")
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
        # one record per station and vehicle class, stamped at the start of the next day like the history sums;
        # the day is valid only if all of its intervals are valid
        valid_time = HISTORY_TIMEZONE.localize(datetime.fromisoformat(date) + timedelta(days=1))

        def _daily_flag(flags) -> int:
            if (flags == 0).any():
                return 0
            return 1 if (flags == 1).all() else 999

        daily = in_df.groupby(["station_code", "variable"])["is_valid"].agg(_daily_flag).reset_index()
        out_entries = []
        for _, row in daily.iterrows():
            out_entries.append(ValidationEntry(
                station=stations_dict[row['station_code']],
                valid_time=valid_time,
                vehicle_class=VehicleClass(row["variable"]),
                entry_class=ValidationTypeClass.VALID,
                entry_value=row["is_valid"],
                period=period
            ))
        return out_entries
