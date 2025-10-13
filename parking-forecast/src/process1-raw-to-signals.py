# SPDX-FileCopyrightText: 2021-2025 STA AG <info@sta.bz.it>
# SPDX-FileContributor: Chris Mair <chris@1006.org>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# ----------------------------------------------------------------------------
#
# Parking occupancy prediction
# process1-raw-to-signals.py
#
# (C) 2021 STA AG
#
# Create a time series with period = 24 * 60 / HOUR_COLS minutes over
# the given interval (see MIN_TS, MAX_TS below).
#
# Add artificial columns hour, dow, month.
#
# Then add holiday information (is_school and is_holiday) and
# 1-day-weather-forecasts (symbol_value), both loaded from CSV files.
#
# Read original CSV files from dir "data-raw/", reindex the data
# to match the time series.
#
# Write out the data to two CSV files having one column for each car park:
# "data-predictors/signals.csv" (NO interpolation, for training) and
# "data-predictors/signals_interpolated.csv" (interpolated, for prediction).
#
# author: Chris Mair - chris@1006.org
#
# changelog:
#
# 2021-07-12 wip
#
# ----------------------------------------------------------------------------

import os
import time
import yaml

from builtins import Exception

import pandas as pd
import csv

# global time range:
MIN_TS = "2022-01-01 00:00:00.000+0000" # arbitrary dawn of time
MAX_TS = time.strftime("%Y-%m-%d", time.gmtime(time.time() + 3600 * 24 * 7)) + " 23:55:00.000+0000" # a week from now


with open("config.yaml", 'r') as stream:
    CONFIG = yaml.safe_load(stream)

# how many distinct values to use for the hour column: 24 (1 hour resolution), 96 (15 min) or 288 (5 min):
HOUR_COLS = CONFIG["HOUR_COLS"]

print("*** %s (HOUR_COLS = %d)" % (os.path.basename(__file__), HOUR_COLS))

t0 = time.time()

for interpolation in (True, False):

    # ----------------------------------------------------------------------------
    # create an index and dataframe that will hold all occupation data

    print("run with interpolation = %s" % interpolation)
    print("create dataframe")

    occupation_ix = pd.date_range(start=MIN_TS,
                                  end=MAX_TS,
                                  freq="300S", name="ts")

    occupation = pd.DataFrame({'ts': occupation_ix})

    # ----------------------------------------------------------------------------
    # add columns hour and dow

    print("add hour, dow and month")

    if HOUR_COLS == 24:
        occupation["hour"] = occupation.ts.dt.hour      # hours since mid night
    elif HOUR_COLS == 96:
        occupation["hour"] = occupation.ts.dt.hour * 4 + occupation.ts.dt.minute // 15    # 15 min intervals since mid night
    elif HOUR_COLS == 288:
        occupation["hour"] = occupation.ts.dt.hour * 12 + occupation.ts.dt.minute // 5    # 5 min intervals since mid night
    else:
        raise Exception("assert failed")

    occupation["dow"] = occupation.ts.dt.dayofweek

    # ----------------------------------------------------------------------------
    # add columns is_school and is_holiday

    print("add is_school and is_holiday")

    # read holiday data
    holidays = pd.read_csv("data-holidays/holidays.csv", parse_dates=True,)
    holidays.ts = pd.to_datetime(holidays.ts)
    holidays = holidays.set_index("ts")
    holidays = holidays.tz_localize('UTC')

    # reindex with occupation index using last value ("pad");
    # make sure holidays.csv covers our data range, otherwise
    # values get copied at the margins

    holidays = holidays.reindex(occupation_ix, method="pad")

    # join to occupation dataframe

    occupation = occupation.join(holidays, on="ts")

    # ----------------------------------------------------------------------------
    # add column month

    occupation["month"] = occupation.ts.dt.month

    # ----------------------------------------------------------------------------
    # add column forecast

    print("add forecast")

    # read forecast data
    forecast = pd.read_csv("data-meteo/meteo.csv", parse_dates=True)
    forecast.tomorrow_date = pd.to_datetime(forecast.tomorrow_date)
    forecast = forecast.set_index("tomorrow_date")
    forecast = forecast.tz_localize('UTC')

    # reindex with occupation index using last value ("pad");
    # make sure forecast.csv covers our data range, otherwise
    # values get copied at the margins

    forecast = forecast.reindex(occupation_ix, method="pad")

    # join to occupation dataframe

    occupation = occupation.join(forecast, on="ts")

    # ----------------------------------------------------------------------------
    # add columns from raw data files

    print("add columns from data files:")

    files = os.listdir("data-raw")
    files.sort()

    for file in files:

        if not file.endswith(".csv"):
            continue

        print("  " + file)

        # read data from file

        fileix = '{0:02d}'.format(int(file[0:2]))
        input_tab = pd.read_csv("data-raw/" + file,
                                parse_dates = True,
                                names=["ts", "occ" + fileix])

        # use the timestamp as index

        input_tab.ts = pd.to_datetime(input_tab.ts)
        input_tab = input_tab.set_index("ts")

        if interpolation:
            # resample to perform linear interpolation (we don't want NaNs)
            input_tab = input_tab.resample("300S", origin=MIN_TS).mean()
            input_tab = input_tab.interpolate()
        else:
            # reindex with occupation index using nearest value at most
            # one period away (other data is set to NaN - we do not want
            # interpolation)
            input_tab = input_tab.reindex(occupation_ix, method="nearest", limit=1)

        # join to occupation dataframe

        occupation = occupation.join(input_tab, on="ts")

    # ----------------------------------------------------------------------------
    # save

    filename = "data-predictors/signals.csv"
    if interpolation:
        filename = "data-predictors/signals_interpolated.csv"

    print("save to %s" % filename)

    occupation.to_csv("%s" % filename, index=False, quoting=csv.QUOTE_ALL)

    t1 = time.time()

    print("done in %.2f seconds" % (t1 - t0))
