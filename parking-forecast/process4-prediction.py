# ----------------------------------------------------------------------------
#
# Parking occupancy prediction
# process4-prediction.py
#
# (C) 2021 STA AG
#
# Read the preprocessed data from data-predictors/signals_interpolated.csv
# and generate the output using the same strategy as process2-signals-to-trainingdata.py.
#
# Starting after LAST_TRAIN_TS, perform prediction using the models trained in
# process3-fit-model.py.
#
# Save the predictions to the file name in the OUTPUT parameter.
#
# author: Chris Mair - chris@1006.org
#
# changelog:
#
# 2021-07-12 wip
#
# ----------------------------------------------------------------------------

import os
import sys
import time
import yaml

from builtins import Exception

import numpy as np
import pandas as pd

import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers.experimental import preprocessing

from parking_utils import *

with open("config.yaml", 'r') as stream:
    CONFIG = yaml.safe_load(stream)

# stop transforming data after this timestamp (must be a multiple of 5 minutes):
LAST_TRAIN_TS = CONFIG["LAST_TRAIN_TS"]

# whether to use the one-hot encoded month as predictor
USE_MONTH = CONFIG["USE_MONTH"]

# model type (DNN or LINEAR):
MODEL_TYPE = CONFIG["MODEL_TYPE"]

# how many hours to predict starting from LAST_TRAIN_TS + 5 minutes:
HOURS_TO_PREDICT = CONFIG["HOURS_TO_PREDICT"]

# how many distinct values to use for the hour column: 24 (1 hour resolution), 96 (15 min) or 288 (5 min):
HOUR_COLS = CONFIG["HOUR_COLS"]

# whether to one-hot encode hour column:
HOUR_ONEHOT = CONFIG["HOUR_ONEHOT"]

# whether to use autoregressive columns for occupation:
USE_AUTOREG_COLS = CONFIG["USE_AUTOREG_COLS"]

# whether to use autoregressive column with 1-day lag (applicable only for USE_AUTOREG_COLS = True)
USE_AUTOREG_COLS_1DAY = CONFIG["USE_AUTOREG_COLS_1DAY"]

# use 7-day mean
USE_7DAY_MEAN = CONFIG["USE_7DAY_MEAN"]

# use 1-day-weather-forecasts:
USE_FORECAST = CONFIG["USE_FORECAST"]

# prediction output file name
OUTPUT = CONFIG["OUTPUT"]

print("*** %s (LAST_TRAIN_TS = %s, USE_MONTH = %s, HOURS_TO_PREDICT = %d, MODEL_TYPE = %s, HOUR_COLS = %d, HOUR_ONEHOT = %s, USE_AUTOREG_COLS = %s, USE_AUTOREG_COLS_1DAY = %s, USE_7DAY_MEAN = %s, USE_FORECAST = %s, OUTPUT = %s)" %
      (os.path.basename(__file__), LAST_TRAIN_TS, USE_MONTH, HOURS_TO_PREDICT, MODEL_TYPE, HOUR_COLS, HOUR_ONEHOT, USE_AUTOREG_COLS, USE_AUTOREG_COLS_1DAY, USE_7DAY_MEAN, USE_FORECAST, OUTPUT))

model_num = 1
if len(sys.argv) > 1:
    model_num = sys.argv[1]

if MODEL_TYPE == "LINEAR":
    model_name = "data-models/linear_model" + str(model_num)
    model = tf.keras.models.load_model(model_name)
elif MODEL_TYPE == "DNN":
    model_name = "data-models/dnn_model" + str(model_num)
    model = tf.keras.models.load_model(model_name)
else:
    raise Exception("sorry, unknown model type, expected: DNN or LINEAR")

# number of columns used for "hour":
hourN = 1
if HOUR_ONEHOT:
    hourN = HOUR_COLS

# ----------------------------------------------------------------------------
# read data and transform to numpy ndarray -> mat_in

print("read data from data-predictors/signals_interpolated.csv:")

signals = pd.read_csv("data-predictors/signals_interpolated.csv", parse_dates=True)
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

print("unroll car parks and build data in the same shape as training data:")

# see process2-signals-to-trainingdata.py for a list of columns
# in mat_in & mat_out

mat_out = np.empty((mat_in.shape[0] * parkN, 55 + hourN-1 + parkN-1 + 1), dtype="float32")
mat_out[:] = np.NaN

t0 = time.time()

ox = 0
for ix in range(0, mat_in.shape[0]):

    if ix < CUTOFF_IX - 8 * 24 * (60 // 5):
        # optimization: as we never access mat_out more than 7 days past the range we're going to predict,
        # don't build the parts older than 8 days before CUTOFF_IX;
        # we could save some memory by not even allocating this part, but mat_out is currently "just" 800 MB
        # vs. about 8 GB used by this script , so the extra work shifting indices wouldn't change much;
        #
        # we still need to increment the target index ox
        ox += parkN
        continue

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
        if USE_AUTOREG_COLS:
            if ix >= 2016:
                mat_out[ox, 49+hourN-1+parkN-1] = mat_in[ix - 2016, 6 + park]                           # "occlag2016"
            if ix >= 288:
                if USE_AUTOREG_COLS_1DAY:
                    mat_out[ox, 50+hourN-1+parkN-1] = mat_in[ix - 288, 6 + park]                        # "occlag288"
                else:
                    mat_out[ox, 50+hourN-1+parkN-1] = 1.0                                               # overwrite autoregressive column with 1-day lag
            if ix >= 12:
                mat_out[ox, 51+hourN-1+parkN-1] = mat_in[ix -   12, 6 + park]                           # "occlag12"
            if ix >= 2:
                mat_out[ox, 52+hourN-1+parkN-1] = mat_in[ix -    2, 6 + park]                           # "occlag2"
            if ix >= 1:
                mat_out[ox, 53+hourN-1+parkN-1] = mat_in[ix -    1, 6 + park]                           # "occlag1"
        else:
            mat_out[ox, 49+hourN-1+parkN-1:54+hourN-1+parkN-1] = 1.0                                    # overwrite all autoregressive colums
        if USE_7DAY_MEAN:
            mat_out[ox, 54+hourN-1+parkN-1] = np.nanmean(mat_in[max(ix-2016, 0):ix+1, 6+park])          # "occmean"
        else:
            mat_out[ox, 54+hourN-1+parkN-1] = 1.0
        mat_out[ox, 55+hourN-1+parkN-1] = mat_in[ix, 6 + park]                                          # "occ"
        ox += 1

# save last value of ``ox''
ox_start_predict = ox

t1 = time.time()

print("  mapped %d out of %d input rows to %d output rows in %.2f seconds" % (CUTOFF_IX, mat_in.shape[0], ox, (t1 - t0)) )
if CUTOFF_IX * parkN != ox:
    raise Exception("assert failed")


# ----------------------------------------------------------------------------
# predict

t0 = time.time()

if USE_AUTOREG_COLS:

    print("predict data (with autoregressive columns) after %s:" % LAST_TRAIN_TS)

    for ix in range(CUTOFF_IX, int(CUTOFF_IX + HOURS_TO_PREDICT * 60 / 5)):
        if (ix - CUTOFF_IX + 1) % 20 == 1:
            print(" doing " + str(ix - CUTOFF_IX + 1) + " / " + str(HOURS_TO_PREDICT * 60 / 5))
        # save value of ox at the start of a new range of car parks
        ox0 = ox
        for park in range(0, parkN):
            mat_out[ox, 0] = mat_in[ix, 2]                                                  # "is_school"
            mat_out[ox, 1] = mat_in[ix, 3]                                                  # "is_holiday"
            if HOUR_ONEHOT:                                                                 # "hour"
                mat_out[ox, 2:2+hourN] = onehot(mat_in[ix, 0], HOUR_COLS)
            else:
                mat_out[ox, 2] = mat_in[ix, 0]
            mat_out[ox, 3+hourN-1:9+hourN] = onehot(mat_in[ix, 1], 7)                       # "dow"
            if USE_MONTH:
                mat_out[ox, 10 + hourN - 1:21 + hourN] = onehot(mat_in[ix, 4] - 1, 12)      # "month"
            else:
                mat_out[ox, 10 + hourN - 1:21 + hourN] = 1.0
            if USE_FORECAST:
                mat_out[ox, 22 + hourN - 1:48 + hourN - 1] = onehot(mat_in[ix, 5], 26)      # "symbol_value"
            else:
                mat_out[ox, 22 + hourN - 1:48 + hourN - 1] = 1.0
            mat_out[ox, 48+hourN-1:48+hourN-1+parkN] = onehot(park, parkN)                  # "parkIndex"
            if ix - 2016 < CUTOFF_IX:
                mat_out[ox, 49+hourN-1+parkN-1] = mat_in[ix - 2016, 6 + park]
            else:
                mat_out[ox, 49+hourN-1+parkN-1] = mat_out[ox - 2016 * parkN, -1]
            if ix - 288 < CUTOFF_IX:
                if USE_AUTOREG_COLS_1DAY:
                    mat_out[ox, 50+hourN-1+parkN-1] = mat_in[ix - 288, 6 + park]
                else:
                    mat_out[ox, 50+hourN-1+parkN-1] = 1.0
            else:
                if USE_AUTOREG_COLS_1DAY:
                    mat_out[ox, 50+hourN-1+parkN-1] = mat_out[ox - 288 * parkN, -1]
                else:
                    mat_out[ox, 50+hourN-1+parkN-1] = 1.0
            if ix - 12 < CUTOFF_IX:
                mat_out[ox, 51+hourN-1+parkN-1] = mat_in[ix - 12, 6 + park]
            else:
                mat_out[ox, 51+hourN-1+parkN-1] = mat_out[ox - 12 * parkN, -1]
            if ix - 2 < CUTOFF_IX:
                mat_out[ox, 52+hourN-1+parkN-1] = mat_in[ix - 2, 6 + park]
            else:
                mat_out[ox, 52+hourN-1+parkN-1] = mat_out[ox - 2 * parkN, -1]
            if ix - 1 < CUTOFF_IX:
                mat_out[ox, 53+hourN-1+parkN-1] = mat_in[ix - 1, 6 + park]
            else:
                mat_out[ox, 53+hourN-1+parkN-1] = mat_out[ox - 1 * parkN, -1]
            if USE_7DAY_MEAN:
                mat_out[ox, 54+hourN-1+parkN-1] = mat_out[ox_start_predict-parkN+park, 54+hourN-1+parkN-1]  # "occmean" (keep using the last value for the given park before predicting)
            else:
                mat_out[ox, 54+hourN-1+parkN-1] = 1.0
            ox += 1

        # at the end of the loop over car parks, call predict once for all of them
        mat_out[ox0: ox0 + parkN, -1:] = model.predict(mat_out[ox0:ox0 + parkN, 0:-1])

    # save last value of ``ox''
    ox_end_predict = ox

    if (CUTOFF_IX + HOURS_TO_PREDICT * 60 / 5) * parkN != ox:
        raise Exception("assert failed")

else:

    print("predict data (w/o autoregressive columns) after %s:" % LAST_TRAIN_TS)

    for ix in range(CUTOFF_IX, int(CUTOFF_IX + HOURS_TO_PREDICT * 60 / 5)):
        if (ix - CUTOFF_IX + 1) % 20 == 1:
            print(" doing " + str(ix - CUTOFF_IX + 1) + " / " + str(HOURS_TO_PREDICT * 60 / 5))
        for park in range(0, parkN):
            mat_out[ox, 0] = mat_in[ix, 2]                                                  # "is_school"
            mat_out[ox, 1] = mat_in[ix, 3]                                                  # "is_holiday"
            if HOUR_ONEHOT:                                                                 # "hour"
                mat_out[ox, 2:2+hourN] = onehot(mat_in[ix, 0], HOUR_COLS)
            else:
                mat_out[ox, 2] = mat_in[ix, 0]
            mat_out[ox, 3+hourN-1:9+hourN] = onehot(mat_in[ix, 1], 7)                       # "dow"
            if USE_MONTH:
                mat_out[ox, 10 + hourN - 1:21 + hourN] = onehot(mat_in[ix, 4] - 1, 12)      # "month"
            else:
                mat_out[ox, 10 + hourN - 1:21 + hourN] = 1.0
            if USE_FORECAST:
                mat_out[ox, 22 + hourN - 1:48 + hourN - 1] = onehot(mat_in[ix, 5], 26)      # "symbol_value"
            else:
                mat_out[ox, 22 + hourN - 1:48 + hourN - 1] = 1.0
            mat_out[ox, 48+hourN-1:48+hourN-1+parkN] = onehot(park, parkN)                  # "parkIndex"
            mat_out[ox, 49+hourN-1+parkN-1:54+hourN-1+parkN-1] = 1.0                        # overwrite sll autoregressive colums
            if USE_7DAY_MEAN:
                mat_out[ox, 54+hourN-1+parkN-1] = mat_out[ox_start_predict-parkN+park, 54+hourN-1+parkN-1]  # "occmean" (keep using the last value for the given park before predicting)
            else:
                mat_out[ox, 54+hourN-1+parkN-1] = 1.0
            ox += 1

    # save last value of ``ox''
    ox_end_predict = ox

    if (CUTOFF_IX + HOURS_TO_PREDICT * 60 / 5) * parkN != ox:
        raise Exception("assert failed")

    mat_out[ox_start_predict:ox_end_predict, -1:] = model.predict(mat_out[ox_start_predict:ox_end_predict, 0:-1])


t1 = time.time()

print("  prediction done in %.2f seconds" % (t1 - t0))

# ----------------------------------------------------------------------------
# saving results

print("save to %s" % OUTPUT)

np.savetxt(OUTPUT, mat_out[ox_start_predict:ox_end_predict, :], fmt="%.2f", delimiter=",")

