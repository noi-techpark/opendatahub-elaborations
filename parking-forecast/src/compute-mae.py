# ----------------------------------------------------------------------------
#
# Parking occupancy prediction
#
# (C) 2022 STA AG
#
# Compute mean absolute error in occupancy prediction
# and write out a CSV file with true occupancy and corresponding
# predictions.
#
# Set THIS_CODE and FUTURE_IX below to pick the car park
# and how much into the future the prediction is to be considered.
#
# For each truth data point available in the requested interval
# MIN_TS .. MAX_TS, interpolate the predicted value at exactly the
# timestamp of the truth data point. Sum the absolute difference
# between the true occupancy value and the predicted occupancy
# value to compute the mean absolute error.
#
# Note that missing truth data is not a problem as we consider
# only the truth data points for the error calculation.
# Truth data in a range where predictions are not (yet) available
# is also skipped.
#
# Finally, there are some days when predictions were not computed
# (due to some problems). To avoid large errors due to the interpolation
# of predicted values spanning many hours or even days, each time
# a prediction would need to be interpolated using an interval of more
# than four hours, the data point is also skipped. The value of
# four hours is chosen such that the gap after midnight when no prediction
# are done does not trigger this case.
#
# example output:
#
#   code = 103
#   future = 1.0 hours
#   min ts = 2022-01-01 00:00:00.000+0000
#   max ts = 2022-06-10 00:00:00.000+0000
#   Retrieving predicted data from database (be patient)...
#   OK, got 3024 rows
#   Looking for raw data files...
#   OK, scode '103' found, file is '00__103__P03_-_Piazza_Walther.csv'
#   OK, got 254830 rows
#   OK, got 41557 rows after filtering time range
#   Looping over rows (be patient)...
#   OK, 41557 total rows checked, 6762 skipped in 22.196 seconds
#   max recorded true occupancy = 403.000
#   mean absolute error = 16.973
#   mean absolute error in percent of max = 4.212
#   file prediction_errors.csv written
#
# author: Chris Mair - chris@1006.org
#
# changelog:
#
# 2022-11-02 complete
# 2022-10-26 created
#
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# user parameters to be set here:
# ----------------------------------------------------------------------------

THIS_CODE = "103"       # Car park code used by ODH (scode).
                        # "103" means Waltherplatz.

FUTURE_IX = 11          # How much time into the future we want the prediction
                        # for (in units of 5 min): 11 means 1 hour, 287 means 24 hours.
                        #
                        # Note the first predicted point is 5 minutes after the full
                        # hour (the full hour being the last truth used).
                        # So, technically index 0 is already 5 minutes into the future and
                        # index 11 is one hour into the future. But practically visibility
                        # of real data in the ODH and computation makes the prediction lag
                        # 11-12 minutes after the full hour before it appears on web01.

                        # Time range we're interested in.
MIN_TS = "2022-01-01 00:00:00.000+0000"
MAX_TS = "2022-06-10 00:00:00.000+0000"

print("code = %s" % THIS_CODE)
print("future = %.1f hours" % ((FUTURE_IX + 1)/12))
print("min ts = %s" % MIN_TS)
print("max ts = %s" % MAX_TS)

# ----------------------------------------------------------------------------

import os
import time
import pandas
from sqlalchemy import create_engine
from builtins import Exception
from parking_utils import *

# consistency check number of car parks
parkN = getParkN()


# ----------------------------------------------------------------------------
# part 1: predictions dataframe
#
# Read predictions offset by FUTURE_IX for carpark THIS_CODE between MIN_TS
# and MAX_TS from the database and provide a function get_interpolated_value_at(ts)
# that returns the interpolated occupancy value at the timestamp ts (or None if it's
# not available.
#
# example: get_interpolated_value_at("2022-01-20 16:30:00+00:00")
# ----------------------------------------------------------------------------

print("Retrieving predicted data from database (be patient)... ")

alchemy_engine = create_engine("postgresql://dwh@127.0.0.1:5432/dwh")
pred_query = '''
with raw as materialized (
    select forecast_start_timestamp as fcts,
           data->'timeseries'->'%s'->%d as data
    from parking_forecast.history
    where forecast_start_timestamp::timestamptz between '%s'::timestamptz and '%s'::timestamptz
)
select (data->>'ts')::timestamptz as ts,
       (data->>'lo')::float4 as lo,
       (data->>'mean')::float4 as occ,
       (data->>'hi')::float4 as hi,
       (data->>'rmse')::float4 as rmse
from raw order by fcts;
''' % (THIS_CODE, FUTURE_IX, MIN_TS, MAX_TS)
pred_df = pandas.read_sql(pred_query, con=alchemy_engine, index_col="ts")

print("OK, got %d rows" % len(pred_df))


def get_interpolated_value_at(ts):
    ts = pandas.to_datetime(ts)
    loix = pred_df.index.get_indexer([ts], method='pad')[0]          # lower index
    upix = pred_df.index.get_indexer([ts], method='backfill')[0]     # upper index
    if loix == -1 or upix == -1:   # out of range
        return None
    if np.isnan(pred_df.occ[loix]) or np.isnan(pred_df.occ[upix]):   # not available
        return None
    x0 = pred_df.index[loix].value / 1.E9   # epoch
    x1 = pred_df.index[upix].value / 1.E9   # epoch
    if abs (x1 - x0) > 4 * 3600:   # too large, consider the prediction to be unavailable
        return None
    x = ts.value / 1.E9
    y0 = pred_df.occ[loix]
    y1 = pred_df.occ[upix]
    if abs(x1 - x0) < 0.001:
        return y0
    y = y0 + (x - x0) * (y1 - y0) / (x1 - x0)
    return y



# ----------------------------------------------------------------------------
# part 2: truth data frame
#
# Read the car park occupancy corresponding to THIS_CODE from data-raw/.
# ----------------------------------------------------------------------------

print("Looking for raw data files...")

raw_files = list(filter(lambda file : file.endswith(".csv"), os.listdir("data-raw/")))
raw_files.sort()

if len(raw_files) != parkN:
    raise Exception("KO: number of stations (%d) != parkN (%d)" % (len(raw_files), parkN))

scode_list = []
scode_file_map = {}

for raw_file in raw_files:
    try:
        pos1 = raw_file.index("__") + 2
        pos2 = raw_file.rindex("__")
    except ValueError:
        raise Exception("KO: cannot extract scode from filename %s" % raw_file)
    scode = raw_file[pos1:pos2]
    scode_list.append(scode)
    scode_file_map[scode] = raw_file

if len(scode_list) != parkN:
    raise Exception("KO: number of scodes (%d) != parkN (%d)" % (len(scode_list), parkN))

if not (THIS_CODE in scode_list):
    raise Exception("KO: requested scode (%s) not found" % THIS_CODE)

print("OK, scode '%s' found, file is '%s'" % (THIS_CODE, scode_file_map[THIS_CODE]))

truth_df = pandas.read_csv("data-raw/%s" % scode_file_map[THIS_CODE], index_col=0,parse_dates=True,names=["ts", "occ"])
print("OK, got %d rows" % len(truth_df))

first_truth = truth_df.index.get_indexer([pandas.to_datetime(MIN_TS)], method='pad')[0]       # index of last row with ts < MIN_TS
last_truth = truth_df.index.get_indexer([pandas.to_datetime(MAX_TS)], method='backfill')[0]  # index of first row with ts > MAX_TS

if first_truth == -1 or last_truth == -1:  # out of range
    raise Exception("KO: MIN_TS/MAX_TS not in range")

truth_df = truth_df.iloc[first_truth:last_truth]
print("OK, got %d rows after filtering time range" % len(truth_df))

# ----------------------------------------------------------------------------
# part 3: loop over all truth values, get the corresponding prediction and
# compute the error.
# ----------------------------------------------------------------------------

print("Looping over rows (be patient)...")

t0 = time.time()

filename = "prediction_errors.csv"
file = open(filename, "w")
file.write("epoch, truth, prediction\n")

cnt_total = 0
cnt_skipped = 0
abs_err = 0.0
max_occ = 0
for row in truth_df.itertuples():
    cnt_total = cnt_total + 1
    pred_val = get_interpolated_value_at(str(row.Index))
    if pred_val == None:
        cnt_skipped = cnt_skipped + 1
        continue
    if  row.occ > max_occ:
        max_occ = row.occ
    abs_err = abs_err + abs(pred_val - row.occ)
    file.write("%.1f, %.1f, %.1f\n" % (row.Index.value/1.E9, row.occ, pred_val))

file.close()

mean_abs_err = abs_err / (cnt_total - cnt_skipped)

t1 = time.time()

print("OK, %d total rows checked, %d skipped in %.3f seconds" % (cnt_total, cnt_skipped, t1 - t0) )
print("max recorded true occupancy = %.3f" % max_occ)
print("mean absolute error = %.3f" % (mean_abs_err) )
print("mean absolute error in percent of max = %.3f" % (100.0 * mean_abs_err / max_occ) )
print("file %s written" % filename)
