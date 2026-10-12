# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Optional
from xml.etree import ElementTree

import pandas as pd

from common.data_model import RoadWeatherObservationMeasureCollection, Station
from common.data_model.roadcast import RoadCastEntry, RoadCastTypeClass, RoadCastClass, ExtendedRoadCastEntry
from road_weather.model.observations import Observations
from common.settings import TMP_DIR, METRO_PYTHON, METRO_BIN, METRO_PARAMETERS_DIR, ROAD_WEATHER_NUM_FORECASTS, \
    ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS, PERIOD_1SEC

logger = logging.getLogger("pollution_v2.road_weather.model.road_weather_model")

# format of the roadcast-time tags in the METRo output, e.g. 2024-08-27T21:20Z (always UTC)
ROADCAST_TIME_FORMAT = "%Y-%m-%dT%H:%M%z"
METRO_TIMEOUT = 300


class RoadConditions(Enum):
    RC1 = "Dry road"
    RC2 = "Wet road"
    RC3 = "Ice / snow on the road"
    RC4 = "Mix water / snow on the road"
    RC5 = "Dew"
    RC6 = "Melting snow"
    RC7 = "Frost"
    RC8 = "Icing rain"

    @staticmethod
    def get_enum_member_value(name: str) -> str | None:
        try:
            return RoadConditions[name].value
        except KeyError:
            return None


class RoadWeatherModel:
    """
    The model for computing road condition. It prepares the METRo inputs (forecast and observations), runs METRo and
    converts the roadcast it produces into entries.
    """

    def compute_data(self, observation: RoadWeatherObservationMeasureCollection,
                     forecast_filename: str,  # TODO: change with RoadWeatherForecastMeasureCollection
                     forecast_start: datetime,
                     station: Station) -> List[ExtendedRoadCastEntry]:
        """
        Compute the road condition for the given station.

        :param observation: The road weather observation measure collection
        :param forecast_filename: The forecast file name
        :param forecast_start: The forecast start
        :param station: The road weather station, with `wrf_code` set
        :return: The list of road conditions
        :raise: ValueError if the observations are not enough for METRo, CalledProcessError if METRo fails
        """
        obs = Observations(self._get_observations_dataframe(observation), station.wrf_code)
        obs.process()
        conf_level = str(obs.conf_level)
        logger.info(f"Computing road condition for station [{station.code}], confidence level {conf_level}")

        with tempfile.TemporaryDirectory(dir=TMP_DIR) as work_dir:
            observation_filename = f"{work_dir}/observation.xml"
            roadcast_filename = f"{work_dir}/roadcast.xml"
            obs.to_xml(observation_filename)
            obs.validate()
            self._run_metro(station, forecast_filename, observation_filename, roadcast_filename, forecast_start,
                            f"{work_dir}/metro.log")
            with open(roadcast_filename, "rb") as f:
                roadcast = f.read()

        entries = []
        for entry in self.parse_roadcast(roadcast, station):
            extended_entry = ExtendedRoadCastEntry(entry.station, entry.valid_time, entry.roadcast_class,
                                                   entry.entry_class, entry.entry_value, entry.period)
            extended_entry.set_conf_level(conf_level)
            entries.append(extended_entry)
        return entries

    @staticmethod
    def _get_observations_dataframe(observation: RoadWeatherObservationMeasureCollection) -> pd.DataFrame:
        """
        The observations in the format expected by `Observations`. Times are UTC, as METRo handles them as such.
        """
        columns = ["time", "prec_qta", "stato_meteo", "temp_aria", "temp_rugiada", "temp_suolo", "vento_vel"]
        df = pd.DataFrame([{
            "time": entry.valid_time.astimezone(timezone.utc).replace(tzinfo=None)
            if entry.valid_time.tzinfo else entry.valid_time,
            **{c: getattr(entry, c) for c in columns[1:]}
        } for entry in observation.get_entries()], columns=columns)
        df[columns[1:]] = df[columns[1:]].apply(pd.to_numeric, errors="coerce")
        # Observations handles 0 as no data for these variables
        nodata_columns = ["temp_aria", "temp_rugiada", "temp_suolo", "vento_vel"]
        df[nodata_columns] = df[nodata_columns].fillna(0)
        return df.sort_values("time", ignore_index=True)

    @staticmethod
    def _run_metro(station: Station, forecast_filename: str, observation_filename: str, roadcast_filename: str,
                   forecast_start: datetime, log_filename: str) -> None:
        metro = [
            METRO_PYTHON, METRO_BIN,
            "--verbose-level", "0",
            "--enable-sunshadow",
            "--sunshadow-method", "1",
            "--use-sst-sensor-depth",
            "--log-file", log_filename,
            "--input-forecast", forecast_filename,
            "--input-observation", observation_filename,
            "--input-station", f"{METRO_PARAMETERS_DIR}/parameters_{station.wrf_code}.xml",
            "--roadcast-start-date", forecast_start.strftime("%Y-%m-%dT%H:%M"),
            "--output-roadcast", roadcast_filename
        ]
        logger.info(f"running {metro}")
        subprocess.run(metro, check=True, capture_output=True, timeout=METRO_TIMEOUT)

    @staticmethod
    def parse_roadcast(roadcast: bytes, station: Station) -> List[RoadCastEntry]:
        """
        Parse the roadcast XML produced by METRo.

        The roadcast has one prediction every few minutes (UTC); one entry is generated for each of the
        ROAD_WEATHER_NUM_FORECASTS forecast steps, ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS minutes apart, starting
        from the first roadcast time. Steps beyond the roadcast horizon are skipped.
        """
        root = ElementTree.fromstring(roadcast)

        rc_by_datetime = {}
        for prediction_element in root.findall(".//prediction-list/prediction"):
            roadcast_time = prediction_element.findtext("roadcast-time")
            rc = prediction_element.findtext("rc")
            if roadcast_time and rc:
                rc_by_datetime[datetime.strptime(roadcast_time.strip(), ROADCAST_TIME_FORMAT)] = (
                    RoadConditions.get_enum_member_value(f"RC{rc.strip()}"))
        if not rc_by_datetime:
            raise ValueError("No predictions found in the roadcast")
        min_roadcast_time = min(rc_by_datetime)

        out_entries = []
        for step in range(1, ROAD_WEATHER_NUM_FORECASTS + 1):
            minutes = step * ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS
            roadcast_time = min_roadcast_time + timedelta(minutes=minutes)

            entry_class = RoadCastTypeClass.get_by_suffix(str(minutes))
            if entry_class is None:
                logger.warning(f"No data type defined for a forecast at {minutes} minutes, skipping")
                continue
            entry_value = rc_by_datetime.get(roadcast_time)
            if entry_value is None:
                logger.debug(f"No road condition for [{station.code}] at {roadcast_time}, skipping")
                continue

            out_entries.append(RoadCastEntry(
                station=station,
                valid_time=roadcast_time,
                roadcast_class=RoadCastClass.ROADCAST,
                entry_class=entry_class,
                entry_value=entry_value,
                period=PERIOD_1SEC
            ))
        return out_entries
