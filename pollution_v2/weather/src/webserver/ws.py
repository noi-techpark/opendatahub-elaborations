# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
import os
import subprocess
from xml.etree import ElementTree

import pandas as pd

from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from pydantic import BaseModel

from common.logging import get_logging_configuration
from common.settings import MAIN_DIR, TMP_DIR, ROADCAST_DIR, PARAMETERS_DIR
from preprocessors.forecast import Forecast
from preprocessors.observations import Observations
from typing import Union, List

logging.config.dictConfig(get_logging_configuration("road-weather"))

logger = logging.getLogger("road-weather.webserver.ws")

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    logging.info("Root endpoint accessed")
    return {"Hello": "World"}


@app.post("/predict/")
async def create_upload_files(station_code: str, files: List[UploadFile] = File(...)):

    parameters_filename = f"{PARAMETERS_DIR}/parameters_{station_code}.xml"
    forecast = Forecast(station_code)
    try:
        with files[0].file as forecast_file:
            forecast.load_xml(forecast_file.read().decode())
            forecast.interpolate_hourly()
            forecast.negative_radiation_filter()
            roadcast_start = forecast.start
            logger.info('forecast - XML processed correctly')
            forecast_filename = f"{TMP_DIR}/forecast_{station_code}_{roadcast_start}.xml"
            forecast.to_xml(forecast_filename)
            logger.info('forecast - XML saved')
        with files[1].file as observations_file:
            tmp_csv_filename = f"{TMP_DIR}/raw-observation_{station_code}.csv"
            observation_filename = f"{TMP_DIR}/observation_{station_code}_{roadcast_start}.xml"
            with open(tmp_csv_filename, mode="w") as file:
                file.write(observations_file.read().decode())
                logger.info('observations - CSV saved')
            try:
                df_obs = pd.read_csv(tmp_csv_filename)

                obs = Observations(df_obs, station_code)
                obs.process()
                obs.to_xml(observation_filename)
                logger.info('observations - XML saved')
                obs.validate()
                logger.info('observations - XML processed correctly')
                conf_level = obs.conf_level
                logger.info(f'confidence level: {conf_level}')
            except ValueError as e:
                # errori di validazione
                logger.error(f'error: {e}')
                raise HTTPException(status_code=400, detail=e)
            except Exception as e:
                # altri tipi di errori
                logger.error(f'error: {e}')
    except Exception as e:
        logger.error(f"error: {e}")

    metro_path = "/usr/local/metro/usr/bin/metro"
    metro_log_path = f"{MAIN_DIR}/metro_forecast.log"
    roadcast_filename = f"{ROADCAST_DIR}/roadcast_{station_code}_{roadcast_start}.xml"

    if forecast_filename and observation_filename and parameters_filename and forecast and roadcast_filename:
        metro = [
            "python3", metro_path,
            "--verbose-level", "0",
            "--enable-sunshadow",
            "--sunshadow-method", "1",
            "--use-sst-sensor-depth",
            "--log-file", metro_log_path,
            "--input-forecast", forecast_filename,
            "--input-observation", observation_filename,
            "--input-station", parameters_filename,
            "--roadcast-start-date", forecast.start,
            "--output-roadcast", roadcast_filename
        ]
        logger.info(f"running {metro}")
        try:
            subprocess.run(metro, check=True)
        except Exception as e:
            logger.error(f'error while executing metro: {e}')
            raise HTTPException(status_code=500, detail=e)
    else:
        logger.warning(f"missing required arguments: 'forecast_filename' = {forecast_filename}, "
                       f"'observation_filename' = {observation_filename}, "
                       f"'parameters_filename' = {parameters_filename}, "
                       f"'forecast' = {forecast}, "
                       f"'roadcast_filename' = {roadcast_filename}")

    if os.path.isfile(roadcast_filename):
        with open(roadcast_filename) as roadcast_file:
            content = roadcast_file.read()
            # adding conf_level
            root = ElementTree.fromstring(content)
            header_element = root.findall('.//header')
            et_conf_level = ElementTree.SubElement(header_element[0], 'conf_level')
            et_conf_level.text = f"{conf_level}"
            return Response(content=ElementTree.tostring(root, encoding='utf8'), media_type="application/xml")
    else:
        raise HTTPException(status_code=500, detail="Cannot process roadcast")
