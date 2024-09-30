# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import datetime
import logging
import time
import urllib
from typing import List

from common.data_model import TrafficSensorStation, RoadWeatherObservationMeasureCollection
from common.model.helper import ModelHelper

import urllib.request
import mimetypes

from common.settings import TMP_DIR

logger = logging.getLogger("pollution_v2.road_weather.model.road_weather_model")


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
                     station: TrafficSensorStation) -> List:
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

        # TODO cablato
        url = f"http://metro:80/predict/?station_code={station.wrf_code}"

        # List of files to upload
        files_to_upload = [forecast_filename, observation_filename]

        # Create multipart form data
        body, boundary = RoadWeatherModel.create_multipart_formdata(files_to_upload)

        # Create a request object
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

        with urllib.request.urlopen(req) as response:
            response_data = response.read()
            print(response_data.decode('utf-8'))  # Print the response from the server

        # validation_data_types = {str(measure.data_type) for measure in validation.measures}
        # traffic_data_types = {str(measure.data_type) for measure in traffic.measures}
        #
        # logger.info(f"{len(validation.measures)} validation measures available "
        #             f"on {len(validation_data_types)} data types")
        # valid_measures = [measure for measure in validation.measures if measure.value == 1]
        # logger.info(f"{len(valid_measures)} "
        #             f"validation measures available computed as valid "
        #             f"on {len(validation_data_types)} data types")
        # logger.info(f"{len(traffic.measures)} traffic measures available "
        #             f"on {len(traffic_data_types)} data types")
        #
        # validated_datetimes = {measure.valid_time for measure in valid_measures}
        # traffic_datetimes = {measure.valid_time for measure in traffic.measures}
        #
        # diff_datetime = {measure.valid_time.strftime("%m/%d/%Y, %H:%M:%S") for measure in traffic.measures
        #                  if measure.valid_time in traffic_datetimes.difference(validated_datetimes)}
        # diff_date = {measure.valid_time.strftime("%m/%d/%Y") for measure in traffic.measures
        #              if measure.valid_time in traffic_datetimes.difference(validated_datetimes)}
        # if len(diff_datetime) > 0:
        #     logger.warning(
        #         f"{len(diff_datetime)} discarded records: no validation "
        #         f"for the dates [{sorted(diff_date)}] on station [{station.code}]) "
        #         f"(and datetimes [{sorted(diff_datetime)}]")
        #
        # run_on_datetimes = validated_datetimes.intersection(traffic_datetimes)
        # logger.info(f"Ready to process pollution computation on {len(run_on_datetimes)} datetimes")
        #
        # traffic_entries = traffic.get_entries()
        #
        # if len(run_on_datetimes) > 0 and len(traffic_entries) > 0:
        #     traffic_df = ModelHelper.get_traffic_dataframe(traffic_entries, run_on_datetimes)
        #     try:
        #         year = sorted({date.strftime("%Y") for date in run_on_datetimes})[-1]
        #     except:
        #         year = ''
        #     pollution_df = copert_emissions(traffic_df, year)
        #     return self._get_pollution_entries_from_df(pollution_df, traffic.get_stations())
        # else:
        #     logger.info("0 validated entries found skipping pollution computation")
        #     return []
