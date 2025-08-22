# ----------------------------------------------------------------------------
#
# Parking occupancy prediction
# process5-generate-json.py
#
# (C) 2022 STA AG
#
# Read:
#
#   - configuration from config.yaml
#   - predictions from the result{N}.csv files (for N = 1, 2, ...)
#   - car park codes ("scode" from ODH) from data-raw/
#
# and generate a web-readable prediction file result.json
#
# author: Chris Mair - chris@1006.org
#
# changelog:
#
# 2022-01-05 created
#
# ----------------------------------------------------------------------------

import os
import time
import yaml
import json
import numpy as np
from datetime import datetime, timezone, timedelta
from rmse import compute_rmse


from builtins import Exception

from parking_utils import *

# ----------------------------------------------------------------------------
# read configuration from config.yaml

with open("config.yaml", 'r') as stream:
    CONFIG = yaml.safe_load(stream)

# stop transforming data after this timestamp (must be a multiple of 5 minutes):
LAST_TRAIN_TS = CONFIG["LAST_TRAIN_TS"]

# how many hours to predict starting from LAST_TRAIN_TS + 5 minutes:
HOURS_TO_PREDICT = CONFIG["HOURS_TO_PREDICT"]

# how many distinct values to use for the hour column: 24 (1 hour resolution), 96 (15 min) or 288 (5 min):
HOUR_COLS = CONFIG["HOUR_COLS"]

# whether to one-hot encode hour column:
HOUR_ONEHOT = CONFIG["HOUR_ONEHOT"]

print("*** %s (LAST_TRAIN_TS = %s, HOURS_TO_PREDICT = %d, HOUR_COLS = %d, HOUR_ONEHOT = %s)" %
      (os.path.basename(__file__), LAST_TRAIN_TS, HOURS_TO_PREDICT, HOUR_COLS, HOUR_ONEHOT))

# number of columns used for "hour"
hourN = 1
if HOUR_ONEHOT:
    hourN = HOUR_COLS

# number of car parks
parkN = getParkN()

# ----------------------------------------------------------------------------
# read predictions from the result{N}.csv files (for N = 1, 2, ...)

t0 = time.time()

# number of result files result{1}.csv, ... result{resN}.csv

resN = 0
while (os.path.isfile("result%d.csv" % (resN + 1) )):
    resN += 1

if resN < 1:
    raise Exception("no result file found")

col_expected = 55 + hourN-1 + parkN-1 + 1
row_expected = HOURS_TO_PREDICT * (60 // 5)

results = [np.ndarray((0, 0))] * resN
for k in range(0, resN):
    results[k] = np.loadtxt("result%d.csv" % (k + 1), delimiter=",")
    if (row_expected * parkN, col_expected) != results[k].shape:
        raise Exception("result file %d has wrong shape" % (k + 1))

t1 = time.time()

print("  %d result files read in %.3f seconds" % (resN, t1 - t0) )


# ----------------------------------------------------------------------------
# read car park codes ("scode" from ODH) from data-raw/

stations = list(filter(lambda file : file.endswith(".csv"), os.listdir('data-raw/')))
stations.sort()

if len(stations) != parkN:
    raise Exception("number of stations (%d) != parkN (%d)" % (len(stations), parkN))

scodes = []

for station in stations:
    try:
        pos1 = station.index("__") + 2
        pos2 = station.rindex("__")
    except ValueError:
        raise Exception("cannot extract scode from filename %s" % station)
    scodes.append(station[pos1:pos2])

if len(scodes) != parkN:
    raise Exception("number of scodes (%d) != parkN (%d)" % (len(scodes), parkN))

print("  %d scode values read" % len(scodes) )

# ----------------------------------------------------------------------------
# generate output

OUTPUT_FILENAME = "result.json"

t0 = time.time()

outdict = { "publish_timestamp":            str(datetime.now(tz=timezone.utc)),
            "forecast_start_timestamp":     str(datetime.fromisoformat(LAST_TRAIN_TS) + timedelta(minutes = 5)),
            "forecast_period_seconds":      300,
            "forecast_duration_hours":      HOURS_TO_PREDICT,
            "model_version":                "1.1",
            "schema_version":               "1.1" }

timeseries = {}

for scode_ix in range(0, len(scodes)):

    this_timeseries = []

    # get the resN time series corresponding to scode_ix

    val = np.ndarray((row_expected, resN))
    for resix in range (0, resN):
        val[:, resix:resix+1] = results[resix][scode_ix::parkN, -1:]
        # consistency check with the one-hot encoded parking index:
        if not np.all(results[resix][scode_ix::parkN, 48 + hourN-1 + scode_ix ] == 1):
            raise Exception("consistency check failed " % ())

    if len(val) != row_expected:
        raise Exception("unexpected length (%d) of time series for scode %s (%d)" % (len(val), scodes[scode_ix], row_expected))

    # compute the RMSE

    rmse = compute_rmse(scodes[scode_ix], outdict["forecast_start_timestamp"][11:19], debug=True)

    # construct dict for JSON;
    # note JSON has no NaN, so we need to convert Numpy NaN to JSON null via Python None
    for line in range (0,row_expected):
        ts = str(datetime.fromisoformat(LAST_TRAIN_TS) + timedelta(minutes = 5 * (line + 1)))
        lo = round(val[line,:].min(), 1)
        if np.isnan(lo):
            lo = None
        mean = round(val[line, :].mean(), 1)
        if np.isnan(mean):
            mean = None
        hi = round(val[line,:].max(), 1)
        if np.isnan(hi):
            hi = None
        r = round(rmse[line], 1)
        if np.isnan(r):
            r = None
        this_timeseries.append({"ts": ts, "lo": lo, "mean": mean, "hi": hi, "rmse": r})

    timeseries[scodes[scode_ix]] = this_timeseries

outdict["timeseries"] = timeseries

fp = open(OUTPUT_FILENAME, "w")
json.dump(outdict, fp)
fp.close()

t1 = time.time()

print("  %s generated in %.3f seconds" % (OUTPUT_FILENAME, t1 - t0) )
