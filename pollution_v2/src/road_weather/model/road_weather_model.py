# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
import os
import time
import urllib
from datetime import datetime, timedelta
from enum import Enum
from typing import List
from xml.etree import ElementTree
from zoneinfo import ZoneInfo

from common.data_model import TrafficSensorStation, RoadWeatherObservationMeasureCollection, Station

import urllib.request

from common.data_model.roadcast import RoadCastEntry, RoadCastTypeClass, RoadCastClass, ExtendedRoadCastEntry
from common.model.helper import ModelHelper
from common.settings import TMP_DIR, METRO_WS_PREDICTION_ENDPOINT, ROAD_WEATHER_NUM_FORECASTS, \
    ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS

logger = logging.getLogger("pollution_v2.road_weather.model.road_weather_model")


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
        except:
            return None


class RoadWeatherModel:
    """
    The model for computing road condition.
    """

    def compute_data(self, observation: RoadWeatherObservationMeasureCollection,
                     forecast_filename: str,  # TODO: change with RoadWeatherForecastMeasureCollection
                     forecast_start: datetime,  # TODO: check if needed
                     station: TrafficSensorStation) -> List[ExtendedRoadCastEntry]:
        """
        Compute the road condition for the given station.
        :param observation: The road weather observation measure collection
        :param forecast_filename: The forecast file name
        :param forecast_start: The forecast start
        :param station: The traffic station
        :return: The list of road conditions
        """

        logger.info(f"Creating observations file from {len(observation.measures)} measures")

        entries = observation.get_entries()
        observation_filename = f"{TMP_DIR}/observations_{round(time.time() * 1000)}.csv"
        with open(observation_filename, 'a') as tmp_csv:
            tmp_csv.write('"time","station_code","prec_qta","stato_meteo",'
                          '"temp_aria","temp_rugiada","temp_suolo","vento_vel"\n')
            for entry in entries:
                tmp_csv.write(f'{entry.valid_time.strftime("%Y-%m-%d %H:%M:%S")},{entry.station.code},{entry.prec_qta},'
                              f'{entry.stato_meteo},{entry.temp_aria},{entry.temp_rugiada},{entry.temp_suolo},'
                              f'{entry.vento_vel}\n')

        logger.info(f"Computing road condition for station [{station.code}] with observations from "
                    f"{observation_filename} and forecast from {forecast_filename}")
        logger.info(f"Forecast start: {forecast_start}")

        url = f"{METRO_WS_PREDICTION_ENDPOINT}{station.wrf_code}"

        # List of files to upload
        files_to_upload = [forecast_filename, observation_filename]

        # Create multipart form data
        body, boundary = ModelHelper.create_multipart_formdata(files_to_upload)

        # Create a request object
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

        response = []
        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read()
                response_content = response_data.decode('utf-8')
                logger.debug(f"server response: \n{response_content}")

                root = ElementTree.fromstring(response_content)
                header_element = root.findall('.//header')[0]
                for tags in header_element:
                    if tags.tag == 'conf_level':
                        conf_level = tags.text
                        logger.info(f"conf level found: {conf_level}")
                        break

                for entry in self._get_entries_from_xml(response_data, conf_level, station):
                    extended_entry = ExtendedRoadCastEntry(entry.station, entry.valid_time, entry.roadcast_class,
                                                           entry.entry_class, entry.entry_value, entry.period)
                    extended_entry.set_conf_level(conf_level)
                    response.append(extended_entry)
        except Exception as e:
            logger.error(f"error while processing request: {e}")

        # Remove temporary files
        for file in files_to_upload:
            os.remove(file)

        return response

    @staticmethod
    def _get_entries_from_xml(response_data, conf_level: str, station: Station) -> List[RoadCastEntry]:

        # TODO cablato
        roadcast_format = '%Y-%m-%dT%H:%M%z'

        root = ElementTree.fromstring(response_data.decode('utf-8'))
        prediction_list_elements = root.findall('.//prediction-list')
        predictions_list = []
        for prediction_list_element in prediction_list_elements:
            for prediction_element in prediction_list_element:
                prediction_dict = {}
                for prediction_value in prediction_element:
                    if prediction_value.tag == 'roadcast-time' or prediction_value.tag == 'rc':
                        prediction_dict[prediction_value.tag] = prediction_value.text
                predictions_list.append(prediction_dict)
        rc_by_datetime = {}
        for prediction in predictions_list:
            rc_by_datetime[datetime.strptime(prediction['roadcast-time'], roadcast_format)] = (
                RoadConditions.get_enum_member_value(f"RC{prediction['rc']}"))
        min_roadcast_time = min([datetime.strptime(prediction['roadcast-time'], roadcast_format)
                                 for prediction in predictions_list])

        tz = ZoneInfo("Europe/Rome")

        out_entries = []
        for delta in range(1, ROAD_WEATHER_NUM_FORECASTS + 1):
            roadcast_time = min_roadcast_time + timedelta(hours=delta)

            minutes = delta * ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS
            out_entries.append(RoadCastEntry(
                station=station,
                valid_time=roadcast_time.replace(tzinfo=tz),
                roadcast_class=RoadCastClass.ROADCAST,
                entry_class=RoadCastTypeClass.get_by_suffix(str(minutes)),
                entry_value=rc_by_datetime.get(roadcast_time),
                period=minutes * ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS
            ))
        [print(entry) for entry in out_entries]
        return out_entries
