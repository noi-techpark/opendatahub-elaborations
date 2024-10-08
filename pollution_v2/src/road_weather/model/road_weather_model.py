# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
import time
import urllib
from datetime import datetime, timedelta
from enum import Enum
from typing import List
from xml.etree import ElementTree

from common.data_model import TrafficSensorStation, RoadWeatherObservationMeasureCollection, Station

import urllib.request
import mimetypes

from common.data_model.roadcast import RoadCastEntry, RoadCastTypeClass, RoadCastClass
from common.settings import TMP_DIR, METRO_WS_PREDICTION_ENDPOINT

logger = logging.getLogger("pollution_v2.road_weather.model.road_weather_model")


# TODO usare?
class RoadConditions(Enum):
    RC1 = "strada asciutta: la quantità di acqua e ghiaccio/neve è minore di 0.2 mm di altezza d’acqua equivalente"
    RC2 = "strada bagnata: la quantità di acqua è maggiore di 0.2 mm"
    RC3 = "ghiaccio/neve: la quantità di ghiaccio/neve è maggiore di 0.2 mm di altezza d’acqua equivalente"
    RC4 = ("misto acqua/neve: le quantità di acqua e ghiaccio/neve sono entrambe maggiori di 0.2 mm di altezza "
           "d’acqua equivalente")
    RC5 = "rugiada: condensa con temperatura della superficie stradale maggiore di 0°C"
    RC6 = "neve sciolta: presenza di precipitazione nevosa con temperatura della superficie stradale maggiore di 0°C"
    RC7 = "ghiaccio da condensa: condensa sulla strada quando la temperatura della superficie stradale è minore di 0°C"
    RC8 = "pioggia ghiacciata: presenza di pioggia quando la temperatura della superficie stradale è minore di 0°C"


class RoadWeatherModel:
    """
    The model for computing road condition.
    """

    @classmethod
    def create_multipart_formdata(cls, files):

        boundary = '----------Boundary'
        lines = []
        for filename in files:
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            lines.append(f'--{boundary}'.encode())
            lines.append(f'Content-Disposition: form-data; name="files"; filename="{filename}"'.encode())
            lines.append(f'Content-Type: {content_type}'.encode())
            lines.append(''.encode())
            with open(filename, 'rb') as f:
                lines.append(f.read())
        lines.append(f'--{boundary}--'.encode())
        lines.append(''.encode())
        body = b'\r\n'.join(lines)
        return body, boundary

    def compute_data(self, observation: RoadWeatherObservationMeasureCollection,
                     forecast_filename: str,  # TODO: change with RoadWeatherForecastMeasureCollection
                     forecast_start: str,  # TODO: check if needed
                     station: TrafficSensorStation) -> List[RoadCastEntry]:
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
        body, boundary = RoadWeatherModel.create_multipart_formdata(files_to_upload)

        # Create a request object
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

        response_data = None
        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read()
                logger.debug(f"server response: \n{response_data.decode('utf-8')}")
                return self._get_entries_from_xml(response_data, station)
        except Exception as e:
            logger.error(f"error while processing request: {e}")
            return []

    @staticmethod
    def _get_entries_from_xml(response_data, station: Station) -> List[RoadCastEntry]:

        # TODO cablati
        # first_forecast_format = '%Y-%m-%dT%H:%M'
        roadcast_format = '%Y-%m-%dT%H:%M%z'

        root = ElementTree.fromstring(response_data.decode('utf-8'))
        # first_forecast_element = root.findall('.//first-roadcast')
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
            rc_by_datetime[datetime.strptime(prediction['roadcast-time'], roadcast_format)] = prediction['rc']
        min_roadcast_time = min([datetime.strptime(prediction['roadcast-time'], roadcast_format)
                                 for prediction in predictions_list])
        out_entries = []
        # TODO 5 cablato
        for delta in range(1, 5):
            roadcast_time = min_roadcast_time + timedelta(hours=delta)

            minutes = delta * 60
            out_entries.append(RoadCastEntry(
                station=station,
                valid_time=roadcast_time,
                roadcast_class=RoadCastClass.ROADCAST,
                entry_class=RoadCastTypeClass.get_by_suffix(str(minutes)),
                entry_value=rc_by_datetime.get(roadcast_time),
                period=minutes * 60
            ))
        [print(entry) for entry in out_entries]
        return out_entries
