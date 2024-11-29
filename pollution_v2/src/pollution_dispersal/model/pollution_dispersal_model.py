# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import datetime
import logging
from typing import List, Dict

import pandas as pd

from common.data_model.common import VehicleClass
from common.data_model.pollution import PollutionEntry, PollutantClass, PollutionMeasureCollection
from common.data_model import TrafficMeasureCollection, TrafficSensorStation
from common.data_model.pollution_dispersal import PollutionDispersalEntry
from common.data_model.validation import ValidationMeasureCollection
from common.data_model.weather import WeatherMeasureCollection
from common.model.helper import ModelHelper
from pollution_connector.model.CopertEmissions import copert_emissions

logger = logging.getLogger("pollution_v2.pollution_connector.model.pollution_dispersal_model")


class PollutionDispersalModel:
    """
    The model for computing pollution data.
    """

    @staticmethod
    def _get_pollution_entries_from_df(dispersal_df: pd.DataFrame, stations_dict: Dict[str, TrafficSensorStation]) -> \
        List[PollutionDispersalEntry]:
        # TODO: implement
        pass

    def compute_data(self, pollution: PollutionMeasureCollection,
                     weather: WeatherMeasureCollection, station: TrafficSensorStation) -> List[PollutionEntry]:

        # TODO: check this compute method implementation (copied from pollution_computation)

        pollution_data_types = {str(measure.data_type) for measure in pollution.measures}
        weather_data_types = {str(measure.data_type) for measure in weather.measures}

        logger.info(f"{len(pollution.measures)} pollution measures available "
                    f"on {len(pollution_data_types)} data types")
        valid_measures = [measure for measure in pollution.measures if measure.value == 1]
        logger.info(f"{len(valid_measures)} "
                    f"pollution measures available computed as valid "
                    f"on {len(pollution_data_types)} data types")
        logger.info(f"{len(weather.measures)} weather measures available "
                    f"on {len(weather_data_types)} data types")

        validated_datetimes = {measure.valid_time for measure in valid_measures}
        weather_datetimes = {measure.valid_time for measure in weather.measures}

        diff_datetime = {measure.valid_time.strftime("%m/%d/%Y, %H:%M:%S") for measure in weather.measures
                         if measure.valid_time in weather_datetimes.difference(validated_datetimes)}
        diff_date = {measure.valid_time.strftime("%m/%d/%Y") for measure in weather.measures
                     if measure.valid_time in weather_datetimes.difference(validated_datetimes)}
        if len(diff_datetime) > 0:
            logger.warning(
                f"{len(diff_datetime)} discarded records: no pollution "
                f"for the dates [{sorted(diff_date)}] on station [{station.code}]) "
                f"(and datetimes [{sorted(diff_datetime)}]")

        run_on_datetimes = validated_datetimes.intersection(weather_datetimes)
        logger.info(f"Ready to process pollution dispersal on {len(run_on_datetimes)} datetimes")

        weather_entries = weather.get_entries()

        if len(run_on_datetimes) > 0 and len(weather_entries) > 0:
            weather_df = ModelHelper.get_weather_dataframe(weather_entries, run_on_datetimes)
            try:
                year = sorted({date.strftime("%Y") for date in run_on_datetimes})[-1]
            except:
                year = ''
            pollution_df = copert_emissions(weather_df, year)
            return self._get_pollution_entries_from_df(pollution_df, weather.get_stations())
        else:
            logger.info("0 validated entries found skipping pollution dispersal")
            return []
