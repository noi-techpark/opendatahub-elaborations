# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd
import pytest

from road_weather.model.observations import Observations

from tests.conftest import DATA_DIR, RW_WRF_CODE


def _raw_observations() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/raw-observation_{RW_WRF_CODE}.csv", parse_dates=["time"])
    return df.drop(columns="station_code")


def _processed(df: pd.DataFrame) -> Observations:
    obs = Observations(df, RW_WRF_CODE)
    obs.process()
    return obs


def test_sst_is_set_at_sunrise_and_sunset_in_utc():
    # CEST (UTC+2): sunset of 2024-08-27 at 20:00 and sunrise of the 28th at 06:30 local time, the times of the
    # observations are UTC. The recorded observations lack the soil temperature around the sunset.
    df = _raw_observations()
    around_sunset = (df["time"] >= "2024-08-27 17:55") & (df["time"] <= "2024-08-27 18:05")
    df.loc[around_sunset, "temp_suolo"] = 20.0

    obs = _processed(df)

    sst_times = obs.df.loc[obs.df["sst"] != 9999, "observation-time"]
    assert list(sst_times) == [pd.Timestamp("2024-08-27 18:00"), pd.Timestamp("2024-08-28 04:30")]


def test_sst_is_nodata_if_soil_temperature_is_missing_at_sunrise_or_sunset():
    # the recorded observations lack the soil temperature at the sunset of the 27th
    df = _raw_observations()
    around_sunrise = (df["time"] >= "2024-08-28 04:20") & (df["time"] <= "2024-08-28 04:40")
    df.loc[around_sunrise, "temp_suolo"] = 0

    obs = _processed(df)

    assert (obs.df["sst"] == 9999).all()
    for t in ("2024-08-27 18:00", "2024-08-28 04:30"):
        assert obs.df.loc[obs.df["observation-time"] == pd.Timestamp(t), "st"].iloc[0] == 9999


def _validated_frame() -> pd.DataFrame:
    times = pd.date_range("2024-01-01 00:00", periods=30, freq="5min")
    df = pd.DataFrame({"observation-time": times, "at": 1.0, "td": 0.5, "pi": 0, "ws": 1.0, "sc": 1,
                       "st": 1.0, "sst": 9999.0})
    df.loc[5, "sst"] = 1.0
    return df


def _validate(df: pd.DataFrame) -> None:
    obs = Observations.__new__(Observations)
    obs.df = df
    obs.validate()


def test_validate_accepts_valid_observations():
    _validate(_validated_frame())


def test_validate_requires_valid_soil_temperature_at_first_or_second_observation():
    df = _validated_frame()
    df.loc[:1, "st"] = 9999
    with pytest.raises(ValueError, match="first or second observation"):
        _validate(df)


def test_validate_accepts_valid_soil_temperature_only_at_second_observation():
    df = _validated_frame()
    df.loc[0, "st"] = 9999
    _validate(df)
