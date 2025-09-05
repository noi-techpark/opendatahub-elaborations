# SPDX-FileCopyrightText: 2021-2025 STA AG <info@sta.bz.it>
# SPDX-FileContributor: Chris Mair <chris@1006.org>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import time
import glob
import psycopg2
import pandas as pd
import numpy as np
from builtins import Exception



def get_forecasts(scode, start_time, debug=False):
    """
    Given a station's scode (e.g. "103"), and a start_time (e.g. "15:05:00") find
    the 2 * 24 * (60/5) = 576 forecasted values from start_time for each day in
    the last 4 weeks (30 - 2 days ago). The upper bound is 2 days ago, because we
    only want past forecasts.
    The function returns a list of up to 28 tuples, each containing the
    forecast_start_timestamp (UTC) and the vector of 576 floats, e.g.:
    ('2022-03-27 15:05:00', [146.1, 145.7, 146.3, 147.4, ...])
    ('2022-03-28 15:05:00', [246.6, 246.5, 244.8, 241.2, ...])
    ...
    """

    t0 = time.time()

    conn = psycopg2.connect("host=127.0.0.1 dbname=dwh user=dwh")

    # note the default is False (!), so even selects keep the session in "idle in transaction",
    # we don't want that

    conn.autocommit = True

    # note there is a sql injection here, because I need the scode inside a json path operator,
    # so make sure scode is trusted

    cur = conn.cursor()
    cur.execute(
        """
          select
               (forecast_start_timestamp::timestamp with time zone at time zone 'UTC')::text as forecast_start_timestamp_utc,
               jsonb_path_query_array(data, ('$.timeseries."' || %s || '"[*].mean')::jsonpath) as mean
          from parking_forecast.history
          where to_char(forecast_start_timestamp::timestamp with time zone at time zone 'UTC', 'HH24:MI:SS') = %s and
          (forecast_start_timestamp::timestamp with time zone) between now() - '30 days'::interval and now() - '2 days'::interval;
        """, (scode, start_time))

    ret = []
    for tup in cur.fetchall():
        ret.append(tup)

    # clean up

    cur.close()
    conn.close()

    t1 = time.time()
    if debug:
        print("get_forecasts(): %d tuples in %f sec" % (len(ret), t1 - t0))

    return ret


def get_groundtruth(scode, debug=False):
    """
    Given a station's scode (e.g. "103"), read its raw data from data-raw/
    and return an interpolated dataframe for some recent interval
    """

    t0 = time.time()

    # get the raw data filename from scode;
    # note there is a filename injection here, so make sure scode is trusted

    files = glob.glob("data-raw/*__" + scode + "__*.csv")
    if debug:
        print("get_groundtruth(): matching raw data files: %s" % files)

    # no file? return empty dataframe

    if len(files) != 1:
        return pd.DataFrame()

    # interpolate

    MIN_TS = "2022-01-01 00:00:00.000+0000"  # arbitrary dawn of time

    tab = pd.read_csv(files[0],
                      parse_dates=True,
                      names=["ts", "occ"])

    # use the timestamp as index

    tab.ts = pd.to_datetime(tab.ts)
    tab = tab.set_index("ts")

    # resample to perform linear interpolation (we don't want NaNs)

    tab = tab.resample("300S", origin=MIN_TS).mean()
    tab = tab.interpolate()

    t1 = time.time()
    if debug:
        print("get_groundtruth(): %d rows in %f sec" % (tab.size, t1 - t0))

    return tab


def compute_rmse(scode, start_time, debug=True):
    """
    Given a station's scode (e.g. "103"), and a start_time (e.g. "15:05:00"),
    get the forecasts and the ground truth for this station and this start time
    in each day of the last 4 weeks (30 - 2 days ago). Compute the RMSE for the
    2 * 24 * (60/5) = 576 forecasted values and return them.
    Example:
        compute_rmse("me:parkhuber", "15:05:00")
    """

    NUM = 2 * 24 * (60//5)
    acc = np.zeros((NUM,))

    try:
        t0 = time.time()

        forecasts = get_forecasts(scode, start_time)
        groundtruth = get_groundtruth(scode)

        # example access syntax:
        # get specific occ value -> groundtruth.loc["2022-04-01 16:00:00+00:00"].occ
        # get index              ->  groundtruth.index.get_loc('2022-04-01 15:50:00+00:00')

        # compute sum of square of errors for all days we have vectors with no NaNs

        cnt = 0

        if len(forecasts) == 0:
            if debug:
                print("compute_rmse(%s, %s): no forecasts, returning NaNs" % (scode, start_time))
            acc[:] = np.NaN
            return acc

        for tup in forecasts:
            ts = tup[0] + "+00:00"
            offset = groundtruth.index.get_loc(ts)
            v1 = groundtruth.iloc[offset:offset + NUM].occ.to_numpy()
            v2 = np.asarray(tup[1], dtype=np.float64)
            if not np.isnan(v1).any() and not np.isnan(v2).any():
                acc = acc + (v1 - v2) ** 2
                cnt = cnt + 1

        # square root of mean
        acc = np.sqrt(acc / cnt)

        t1 = time.time()
        if debug:
            print("compute_rmse(%s, %s): %d/%d days in %f sec" % (scode, start_time, cnt, len(forecasts), t1 - t0))

        return acc

    except:

        if debug:
            print("compute_rmse(%s, %s): exception, returning NaNs" % (scode, start_time))
        acc[:] = np.NaN
        return acc

