# SPDX-FileCopyrightText: 2021-2025 STA AG <info@sta.bz.it>
# SPDX-FileContributor: Chris Mair <chris@1006.org>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# ----------------------------------------------------------------------------
#
# Parking occupancy prediction
# process3-fit-model.py
#
# (C) 2021 STA AG
#
# Read the preprocessed data from data-predictors/trainingdata_nonan.csv
# and train a linear or a DNN regression model using Keras from TF2.
#
# Reference: https://www.tensorflow.org/tutorials/keras/regression
#
# author: Chris Mair - chris@1006.org
#
# changelog:
#
# 2021-12-08 wip
#
# ----------------------------------------------------------------------------

import os
import sys
import time
import yaml

from builtins import Exception

import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers.experimental import preprocessing

from parking_utils import *

with open("config.yaml", 'r') as stream:
    CONFIG = yaml.safe_load(stream)

# whether to use the one-hot encoded month as predictor
USE_MONTH = CONFIG["USE_MONTH"]

# model type (DNN or LINEAR):
MODEL_TYPE = CONFIG["MODEL_TYPE"]

# how many epochs to train (typical values: 2 - 20):
EPOCHS = CONFIG["MODEL_EPOCHS"]

# how many distinct values to use for the hour column: 24 (1 hour resolution), 96 (15 min) or 288 (5 min):
HOUR_COLS = CONFIG["HOUR_COLS"]

# whether to one-hot encode hour column:
HOUR_ONEHOT = CONFIG["HOUR_ONEHOT"]

# whether to use autoregressive columns for occupation:
USE_AUTOREG_COLS = CONFIG["USE_AUTOREG_COLS"]

# whether to use autoregressive column with 1-day lag (applicable only for USE_AUTOREG_COLS = True)
USE_AUTOREG_COLS_1DAY = CONFIG["USE_AUTOREG_COLS_1DAY"]

# the amount of (relative) noise to add to the autoregressive columns for occupation:
AUTOREG_NOISE = CONFIG["AUTOREG_NOISE"]

print("*** %s (USE_MONTH = %s, MODEL_TYPE = %s, EPOCHS = %d, HOUR_COLS = %d, HOUR_ONEHOT = %s, USE_AUTOREG_COLS = %s, USE_AUTOREG_COLS_1DAY = %s, AUTOREG_NOISE = %f)" %
      (os.path.basename(__file__), USE_MONTH, MODEL_TYPE, EPOCHS, HOUR_COLS, HOUR_ONEHOT, USE_AUTOREG_COLS, USE_AUTOREG_COLS_1DAY, AUTOREG_NOISE))


# ----------------------------------------------------------------------------

# initialize RNG from entropy pool

rg = np.random.default_rng(seed=None)   # docs about seed: "If None, then fresh, unpredictable entropy will be pulled from the OS."

# ----------------------------------------------------------------------------

# read preprocessed training data

dataset = pd.read_csv("data-predictors/trainingdata_nonan.csv", header=None, dtype="float16")

parkN = getParkN()  # number of car parks

hourN = 1           # number of columns used for "hour"
if HOUR_ONEHOT:
    hourN = HOUR_COLS

arix = 49 + hourN - 1 + parkN - 1   # autoreg. column index
arnum = 5                           # autoreg. column count
if USE_AUTOREG_COLS:
    # add noise to the five autoregressive colums
    dataset.values[:, arix:arix + arnum] *= (1 - AUTOREG_NOISE) + (AUTOREG_NOISE * 2.0) * rg.random((dataset.shape[0], arnum))
    if not USE_AUTOREG_COLS_1DAY:
        # overwrite just the 1-day lag column with 1.0
        dataset.values[:, arix + 1] = 1.0
else:
    # overwrite all autoregressive colums
    dataset.values[:, arix:arix + arnum] = 1.0

# ----------------------------------------------------------------------------

COLS = dataset.shape[1]

# use 98% of data for training and 2% for final evaluation of result

train_dataset = dataset.sample(frac=0.98, random_state=int(2E9 * rg.random()))
test_dataset = dataset.drop(train_dataset.index)
del dataset

train_features = train_dataset
test_features = test_dataset

train_labels = train_features.pop(COLS - 1)
test_labels = test_features.pop(COLS - 1)

# normalization

normalizer = preprocessing.Normalization()
normalizer.adapt(np.array(train_features))


# --- linear model -----------------------------------------------------------


def do_linear():

    t0 = time.time()

    linear_model = tf.keras.Sequential([
        normalizer,
        layers.Dense(units=1)
    ])

    linear_model.compile(
        optimizer=tf.optimizers.Adam(learning_rate=0.01),
        loss='mean_absolute_error')

    linear_model.summary()

    linear_model.fit(
        train_features, train_labels,
        epochs=EPOCHS,
        shuffle=True,
        verbose=2,
        validation_split = 0.2)

    print("Mean absolute error (linear model):")
    print(linear_model.evaluate(test_features, test_labels, verbose=0))

    linear_model.save("data-models/linear_model")

    t1 = time.time()
    print("linear model done in %.2f seconds)" % (t1 - t0))


# --- DNN model --------------------------------------------------------------

def do_dnn():

    t0 = time.time()

    # ---
    # BEGIN - we tried embedding, but gave up (2021-06-29)
    # hours_input = layers.Input(shape=(1,), dtype=tf.float32)
    # hours_embedding = layers.Embedding(input_dim=24 * 4, output_dim=24)(hours_input)
    # hours_embedding = keras.layers.Flatten()(hours_embedding)
    #
    # # define layers and model
    # concat = layers.concatenate([hours_embedding, normalizer])
    #
    # hidden1 = layers.Dense(128, activation="relu")(concat)
    # hidden2 = layers.Dense(64, activation="relu")(hidden1)
    # hidden3 = layers.Dense(32, activation="relu")(hidden2)
    # output = layers.Dense(1)(hidden3)
    # dnn_model = keras.Model(inputs=[hours_input, station_input, efa_input, day_type_input], outputs=[output])
    # model.compile(loss="mean_absolute_error", optimizer="adam")
    # END - we tried embedding, but gave up (2021-06-29)
    # ---

    dnn_model = keras.Sequential([
        # added layer with respect to example
        normalizer,
        layers.Dense(128, activation='relu'),
        layers.Dense(64, activation='relu'),
        layers.Dense(32, activation='relu'),
        layers.Dense(1)
    ])

    dnn_model.compile(
        # changed optimizer from Adam to SGD:
        # optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        optimizer=tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.8, decay=0.005),
        loss = 'mean_absolute_error'
    )

    dnn_model.summary()

    dnn_model.fit(
        train_features, train_labels,
        epochs=EPOCHS,
        # changed batch_size from default (32), shuffle=True should be the default anyway
        batch_size=128,
        shuffle=True,
        verbose=2,
        validation_split=0.2)


    print("Mean absolute error (DNN model):")
    print(dnn_model.evaluate(test_features, test_labels, verbose=0))

    model_num = 1
    if len(sys.argv) > 1:
        model_num = sys.argv[1]

    model_name = "data-models/dnn_model" + str(model_num)
    dnn_model.save(model_name)

    t1 = time.time()
    print("DNN model done in %.2f seconds and saved as %s)" % (t1 - t0, model_name))


# --- run --------------------------------------------------------------------

if MODEL_TYPE == "LINEAR":
    do_linear()
elif MODEL_TYPE == "DNN":
    do_dnn()
else:
    raise Exception("sorry, unknown model type, expected: DNN or LINEAR")
