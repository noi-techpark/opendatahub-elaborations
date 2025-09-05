# SPDX-FileCopyrightText: 2021-2025 STA AG <info@sta.bz.it>
# SPDX-FileContributor: Chris Mair <chris@1006.org>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# ----------------------------------------------------------------------------
#
# Parking occupancy prediction
# process2-signals-to-trainingdata.py
#
# (C) 2021 STA AG
#
# Read the preprocessed data from data-predictors/signals.csv
# and build the training data matrix with predictors and response up to
# and including LAST_TRAIN_TS (see below for a description of the columns).
#
# Save the matrix to: "data-predictors/trainingdata_nonan.csv" for input in
# the regression learning step.
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
import numpy as np

from parking_utils import *

with open("config.yaml", 'r') as stream:
    CONFIG = yaml.safe_load(stream)

# stop transforming data after this timestamp (must be a multiple of 5 minutes):
LAST_TRAIN_TS = CONFIG["LAST_TRAIN_TS"]

# whether to use the one-hot encoded month as predictor
USE_MONTH = CONFIG["USE_MONTH"]

# how many distinct values to use for the hour column: 24 (1 hour resolution), 96 (15 min) or 288 (5 min):
HOUR_COLS = CONFIG["HOUR_COLS"]

# whether to one-hot encode hour column:
HOUR_ONEHOT = CONFIG["HOUR_ONEHOT"]

# whether to one-hot encode hour column:
USE_7DAY_MEAN = CONFIG["USE_7DAY_MEAN"]

# use 1-day-weather-forecasts:
USE_FORECAST = CONFIG["USE_FORECAST"]

print("*** %s (LAST_TRAIN_TS = %s, USE_MONTH = %s, HOUR_COLS = %d, HOUR_ONEHOT = %s, USE_7DAY_MEAN = %s, USE_FORECAST = %s)" % (os.path.basename(__file__), LAST_TRAIN_TS, USE_MONTH, HOUR_COLS, HOUR_ONEHOT, USE_7DAY_MEAN, USE_FORECAST))

# number of columns used for "hour":
hourN = 1
if HOUR_ONEHOT:
    hourN = HOUR_COLS

# ----------------------------------------------------------------------------
# read data and transform to numpy ndarray -> mat_in

print("read data from signals.csv:")

signals = pd.read_csv("data-predictors/signals.csv", parse_dates=True)
signals.ts = pd.to_datetime(signals.ts)
signals = signals.set_index("ts")
mat_in = signals.values

parkN = getParkN()  # number of car parks
if parkN != mat_in.shape[1] - 6:
    raise Exception("assert failed")

print ("  %d car parks read" % parkN)

# index of first timestamp after LAST_TRAIN_TS:
CUTOFF_IX = signals.index.get_loc(pd.to_datetime(LAST_TRAIN_TS)) + 1

# ----------------------------------------------------------------------------
# loop over mat_in and build to mat_out

print("unroll car parks and build training data:")

# mat_in:
#  "ts" -> pandas index, not in mat_in
#  "hour"         ->  0
#  "dow"          ->  1 (values 0 .. 6)
#  "is_school"    ->  2
#  "is_holiday"   ->  3
#  "month"        ->  4 (values 1 .. 12)
#  "symbol_value" ->  5
#  "occ00"        ->  6
#  "..."
#  "occParkN-1"   ->  6 + monthN + parkN-1

# mat_out:
#  "is_school"   ->   0
#  "is_holiday"  ->   1
#  "hour"        ->   2           ..  2 + hourN-1               hour, can be single col or one-hot encoded (0 .. hourN-1)
#  "dow"         ->   3 + hourN-1 ..  9 + hourN-1               dow, one-hot encoded
#  "month"       ->  10 + hourN-1 .. 21 + hourN-1               month, one-hot encoded
#  "forecast"    ->  22 + hourN-1 .. 47 + hourN-1               forecast (0..25), one-hot encoded
#  "parkIndex"   ->  48 + hourN-1 .. 48 + hourN-1 + parkN-1     car park index, one-hot encoded (0 .. parkN-1)
#  "occlag2016"  ->  49 + hourN-1 + parkN-1                     lag 1 week
#  "occlag288"   ->  50 + hourN-1 + parkN-1                     lag 1 day
#  "occlag12"    ->  51 + hourN-1 + parkN-1                     lag 1 hour
#  "occlag2"     ->  52 + hourN-1 + parkN-1                     lag 10 minutes
#  "occlag1"     ->  53 + hourN-1 + parkN-1                     lag 5 minutes
#  "occmean"     ->  54 + hourN-1 + parkN-1                     running average of the last 7 days
#  "occ"         ->  55 + hourN-1 + parkN-1                     current occupation (response)

mat_out = np.empty((mat_in.shape[0] * parkN, 55 + hourN-1 + parkN-1 + 1), dtype="float32")
mat_out[:] = np.NaN

t0 = time.time()

ox = 0
for ix in range(0, mat_in.shape[0]):
    if ix == CUTOFF_IX:
        break
    for park in range(0, parkN):
        mat_out[ox, 0] = mat_in[ix, 2]                                                                  # "is_school"
        mat_out[ox, 1] = mat_in[ix, 3]                                                                  # "is_holiday"
        if HOUR_ONEHOT:                                                                                 # "hour"
            mat_out[ox, 2:2+hourN] = onehot(mat_in[ix, 0], HOUR_COLS)
        else:
            mat_out[ox, 2] = mat_in[ix, 0]
        mat_out[ox, 3+hourN-1:9+hourN] = onehot(mat_in[ix, 1], 7)                                       # "dow"
        if USE_MONTH:
            mat_out[ox, 10 + hourN-1:21 + hourN] = onehot(mat_in[ix, 4] - 1, 12)                        # "month"
        else:
            mat_out[ox, 10 + hourN - 1:21 + hourN] = 1.0
        if USE_FORECAST:
            mat_out[ox, 22 + hourN - 1:48 + hourN - 1] = onehot(mat_in[ix, 5], 26)                      # "symbol_value"
        else:
            mat_out[ox, 22 + hourN - 1:48 + hourN - 1] = 1.0
        mat_out[ox, 48+hourN-1:48+hourN-1+parkN] = onehot(park, parkN)                                  # "parkIndex"
        if ix >= 2016:
            mat_out[ox, 49+hourN-1+parkN-1] = mat_in[ix - 2016, 6 + park]                               # "occlag2016"
        if ix >= 288:
            mat_out[ox, 50+hourN-1+parkN-1] = mat_in[ix -  288, 6 + park]                               # "occlag288"
        if ix >= 12:
            mat_out[ox, 51+hourN-1+parkN-1] = mat_in[ix -   12, 6 + park]                               # "occlag12"
        if ix >= 2:
            mat_out[ox, 52+hourN-1+parkN-1] = mat_in[ix -    2, 6 + park]                               # "occlag2"
        if ix >= 1:
            mat_out[ox, 53+hourN-1+parkN-1] = mat_in[ix -    1, 6 + park]                               # "occlag1"
        if USE_7DAY_MEAN:
            mat_out[ox, 54+hourN-1+parkN-1] = np.nanmean(mat_in[max(ix - 2016, 0):ix + 1, 6+park])      # "occmean"
        else:
            mat_out[ox, 54 + hourN - 1 + parkN - 1] = 1.0

        mat_out[ox, 55+hourN-1+parkN-1] = mat_in[ix, 6 + park]                                          # "occ"
        ox += 1

ox_end = ox

t1 = time.time()

print("  mapped %d out of %d input rows to %d output rows in %.2f seconds" % (CUTOFF_IX, mat_in.shape[0], ox, (t1 - t0)) )
if CUTOFF_IX * parkN != ox:
    raise Exception("assert failed")

# ----------------------------------------------------------------------------
# save

t0 = time.time()

print("save to data-predictors/trainingdata_nonan.csv:")

# just save up to including LAST_TRAIN_TS, below are NaNs anyway
mat_out = mat_out[:ox_end, :]

# for debugging, uncomment this to save the complete data, including NaNs:
# np.savetxt("data-predictors/trainingdata_complete.csv", mat_out, fmt="%.0f", delimiter=",")

mat_out = mat_out[~np.isnan(mat_out).any(axis=1)]       # remove NaNs
np.savetxt("data-predictors/trainingdata_nonan.csv", mat_out, fmt="%.0f", delimiter=",")

t1 = time.time()
print("  saved in %.2f seconds" % (t1 - t0))

