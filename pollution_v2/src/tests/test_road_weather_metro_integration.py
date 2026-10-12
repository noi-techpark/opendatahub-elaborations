# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Runs the road weather model with the real METRo, with recorded forecast and observations of a station. Skipped where
METRo is not installed, i.e. outside the job image:

    docker build -f infrastructure/docker/Dockerfile --target build -t pollution-v2 .
    docker run --rm --entrypoint python pollution-v2 -m pytest tests/test_road_weather_metro_integration.py
"""
import os
from datetime import datetime, timezone

import pytest

from common.data_model import RoadWeatherObservationMeasureCollection
from common.settings import METRO_BIN, METRO_PYTHON
from road_weather.model import road_weather_model
from road_weather.model.road_weather_model import RoadWeatherModel, RoadConditions

from tests.conftest import DATA_DIR, RW_FORECAST_START, load_observation_measures, make_station

pytestmark = pytest.mark.skipif(not (os.path.exists(METRO_BIN) and os.path.exists(METRO_PYTHON)),
                                reason="METRo not installed")


@pytest.fixture(autouse=True)
def _tmp_dir(tmp_dir):
    pass


def test_real_metro_roadcast_for_recorded_station_data():
    station = make_station()
    observations = RoadWeatherObservationMeasureCollection(load_observation_measures(station))

    entries = RoadWeatherModel().compute_data(observations, str(DATA_DIR / "forecast_101.xml"), RW_FORECAST_START,
                                              station)

    assert len(entries) == road_weather_model.ROAD_WEATHER_NUM_FORECASTS
    assert {e.conf_level for e in entries} <= {"0", "1"}
    assert {e.entry_value for e in entries} <= {c.value for c in RoadConditions}
    # roadcast starts at the forecast start (2024-08-27 21:00 UTC) and runs hourly
    assert entries[0].valid_time.utcoffset().total_seconds() == 0
    assert datetime(2024, 8, 27, 21, 0, tzinfo=timezone.utc) < entries[0].valid_time <= datetime(
        2024, 8, 27, 23, 0, tzinfo=timezone.utc)
    assert {b.valid_time - a.valid_time for a, b in zip(entries, entries[1:])} == {
        entries[1].valid_time - entries[0].valid_time}
