#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from preprocessors.observations import Observations
from preprocessors.forecast import Forecast
import urllib.request
import pandas as pd
import subprocess
import argparse
import os

# -----------------------------------------------------------------------------
# Arguments
# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='get input and run METRo')
parser.add_argument('station_code', type=str, help='Road weather station code [101-123]')
args = parser.parse_args()
maindir = ".."
print(maindir)
print(f'Road weather station {args.station_code}')

# -----------------------------------------------------------------------------
# Parameters
# -----------------------------------------------------------------------------
# URL del file XML da scaricare
params_url = f"https://www.cisma.bz.it/wrf-alpha/CR/station_{args.station_code}.xml"
parameters_filename = f"{maindir}/data/parameters/parameters_{args.station_code}.xml"
# Verifica se il file XML parametri è già presente
if not os.path.exists(parameters_filename):
    # download file XML parametri
    urllib.request.urlretrieve(params_url, parameters_filename)
    print('* parameters - XML saved')
else:
    print('* parameters - XML alredy exists')

# -----------------------------------------------------------------------------
# Forecast
# -----------------------------------------------------------------------------
forecast = Forecast(args.station_code)
forecast.download_xml(f"https://www.cisma.bz.it/wrf-alpha/CR/{args.station_code}.xml")
forecast.interpolate_hourly()
forecast.negative_radiation_filter()
roadcast_start = forecast.start
print('* forecast - XML processed correctly')
forecast_filename = f"{maindir}/data/forecast/forecast_{args.station_code}_{roadcast_start}.xml"
forecast.to_xml(forecast_filename)
print('* forecast - XML saved')

# -----------------------------------------------------------------------------
# Observations
# -----------------------------------------------------------------------------
try:
    ### !!! ###
    # Qui va definito il dataframe contenente i dati osservati dalle stazioni roadweather
    # df_obs deve contenere i campi: time, prec_qta, stato_meteo, temp_aria, temp_rugiada, temp_suolo, vento_vel
    # La finestra temporale di dati osservati è definita sulla base di forecast.start:
    # start_obs = forecast.start - 16 h
    # end_obs = forecast.start + 8 h
    # Esempio:
    # df_obs = get_obs_data(args.station_code, start_obs, end_obs)
    ### !!! ###
    df_obs = pd.read_csv(f'./data/raw-observation_{args.station_code}.csv')

    obs = Observations(df_obs, args.station_code)
    obs.process()
    observation_filename = f"{maindir}/data/observation/observation_{args.station_code}_{roadcast_start}.xml"
    obs.to_xml(observation_filename)
    print('* observations - XML saved')
    obs.validate()
    print('* observations - XML processed correctly')
    conf_level = obs.conf_level
    print(f'* confidence level: {conf_level}')
except ValueError as e:
    # errori di validazione
    print(f'error: {e}')
except Exception as e:
    # altri tipi di errori
    print(f'error: {e}')

# -----------------------------------------------------------------------------
# Run METRo
# -----------------------------------------------------------------------------
METRo_path=f"{maindir}/metro/usr/share/metro/metro.py"
METRo_log_path=f"{maindir}/data/METRo-log/METRo_forecast.log"
roadcast_filename = f"{maindir}/data/roadcast/roadcast_{args.station_code}_{roadcast_start}.xml"

METRo = [
    "python3", METRo_path,
    "--verbose-level", "0",
    "--enable-sunshadow",
    "--sunshadow-method", "1",
    "--use-sst-sensor-depth",
    "--log-file", METRo_log_path,
    "--input-forecast", forecast_filename,
    "--input-observation", observation_filename,
    "--input-station", parameters_filename,
    "--roadcast-start-date", forecast.start,
    "--output-roadcast", roadcast_filename
]
subprocess.run(METRo, check=True)
