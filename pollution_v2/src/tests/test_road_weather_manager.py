# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import subprocess
from datetime import datetime, timedelta, timezone

import pytest

from common.cache.computation_checkpoint import ComputationCheckpoint, ComputationCheckpointCache
from common.data_model import Provenance
from road_weather.manager.road_weather import RoadWeatherManager
from road_weather.model import road_weather_model

from tests.conftest import (FakeConnector, FakeConnectorCollector, RW_FORECAST_START, RW_STATION_CODE, RW_WRF_CODE,
                            load_observation_measures, make_station)

pytestmark = pytest.mark.usefixtures("tmp_dir", "forecast_url")


@pytest.fixture
def checkpoint_cache(tmp_path) -> ComputationCheckpointCache:
    return ComputationCheckpointCache(str(tmp_path / "checkpoint.db"))


@pytest.fixture
def connectors() -> FakeConnectorCollector:
    return FakeConnectorCollector(FakeConnector(measures=load_observation_measures(make_station())))


@pytest.fixture
def manager(connectors, checkpoint_cache) -> RoadWeatherManager:
    return RoadWeatherManager(connectors, Provenance(None, "test", "test", "0"), checkpoint_cache)


def _checkpoint(checkpoint_cache, station) -> datetime:
    checkpoint = checkpoint_cache.get(ComputationCheckpoint.get_id_for_station(station, "ROAD_WEATHER"))
    return checkpoint.checkpoint_dt if checkpoint else None


def test_computes_and_uploads_forecast_and_conf_level(manager, connectors, checkpoint_cache, tmp_dir, fake_metro):
    station = make_station()

    n = manager.run_computation_for_single_station(station)

    # 45 forecasts, hourly from 22:20 UTC; the recorded observations last until 04:46 of the next day, so the first
    # 7 forecasts are already covered by observations and are not uploaded
    assert n == road_weather_model.ROAD_WEATHER_NUM_FORECASTS - 7
    forecast = connectors.road_weather_forecast.posted_measures
    assert len(forecast) == n
    assert {m.station.code for m in forecast} == {RW_STATION_CODE}
    assert {m.data_type.name.split("-")[0] for m in forecast} == {"ROADCAST"}
    assert len({m.data_type.name for m in forecast}) == n  # one data type per forecast step
    assert all(isinstance(m.value, str) and m.value for m in forecast)
    assert {m.period for m in forecast if m.data_type.name.endswith("FORECAST_1200")} == {72000}
    assert all(m.provenance.provenance_id == "prov-new" for m in forecast)

    conf = connectors.road_weather_conf_level.posted_measures
    assert len(conf) == 1
    assert conf[0].data_type.name.endswith("RW_FORECAST_CONF_LEVEL")
    assert conf[0].value == "0"  # the recorded observations lack data
    assert conf[0].period == 1

    assert connectors.road_weather_forecast.posted_data_types  # data types are created
    assert _checkpoint(checkpoint_cache, station) == RW_FORECAST_START
    assert list(tmp_dir.iterdir()) == []  # no leftover forecast/observation files


def test_observation_window_follows_forecast_start_in_utc(manager, connectors, fake_metro):
    manager.run_computation_for_single_station(make_station())

    (from_date, to_date), = connectors.road_weather_observation.requested_intervals
    assert from_date == RW_FORECAST_START - timedelta(hours=16) == datetime(2024, 8, 27, 5, 0, tzinfo=timezone.utc)
    assert to_date == RW_FORECAST_START + timedelta(hours=8)


def test_only_forecasts_after_latest_observation_are_uploaded(manager, connectors, fake_metro):
    # observations until 2024-08-28 04:46 UTC: ODH refuses data older than the latest one, so the forecasts
    # of the first hours are dropped
    manager.run_computation_for_single_station(make_station())

    valid_times = [m.valid_time for m in connectors.road_weather_forecast.posted_measures]
    assert min(valid_times) > datetime(2024, 8, 28, 4, 46, tzinfo=timezone.utc)


def test_forecast_already_processed_is_skipped(manager, connectors, fake_metro):
    station = make_station()
    assert manager.run_computation_for_single_station(station) > 0
    runs_before = len(fake_metro.calls)
    posted_before = len(connectors.road_weather_forecast.posted_measures)

    assert manager.run_computation_for_single_station(station) == 0

    assert len(fake_metro.calls) == runs_before  # METRo not called again
    assert len(connectors.road_weather_forecast.posted_measures) == posted_before


def test_newer_forecast_is_processed(manager, checkpoint_cache, fake_metro):
    station = make_station()
    checkpoint_cache.set(ComputationCheckpoint(RW_STATION_CODE, RW_FORECAST_START - timedelta(hours=6), "ROAD_WEATHER"))

    assert manager.run_computation_for_single_station(station) > 0
    assert _checkpoint(checkpoint_cache, station) == RW_FORECAST_START


def test_checkpoints_are_per_station(manager, checkpoint_cache, fake_metro):
    other = make_station(code="2022")
    checkpoint_cache.set(ComputationCheckpoint("2022", RW_FORECAST_START, "ROAD_WEATHER"))

    assert manager.run_computation_for_single_station(make_station()) > 0
    assert _checkpoint(checkpoint_cache, other) == RW_FORECAST_START


def test_works_without_checkpoint_cache(connectors, fake_metro):
    manager = RoadWeatherManager(connectors, Provenance(None, "test", "test", "0"))
    assert manager.run_computation_for_single_station(make_station()) > 0
    assert manager.run_computation_for_single_station(make_station()) > 0  # nothing to skip on


def test_no_observations_uploads_nothing_and_retries_next_time(checkpoint_cache, tmp_dir, fake_metro):
    connectors = FakeConnectorCollector(FakeConnector(measures=[]))
    manager = RoadWeatherManager(connectors, Provenance(None, "test", "test", "0"), checkpoint_cache)
    station = make_station()

    assert manager.run_computation_for_single_station(station) == 0

    assert fake_metro.calls == []
    assert connectors.road_weather_forecast.posted_measures == []
    assert connectors.road_weather_forecast.posted_provenances == []
    assert _checkpoint(checkpoint_cache, station) is None
    assert list(tmp_dir.iterdir()) == []


def test_metro_failure_propagates_without_checkpoint(manager, connectors, checkpoint_cache, failing_metro, tmp_dir):
    station = make_station()

    with pytest.raises(subprocess.CalledProcessError):
        manager.run_computation_for_single_station(station)

    assert connectors.road_weather_forecast.posted_measures == []
    assert _checkpoint(checkpoint_cache, station) is None  # computed again at the next run
    assert list(tmp_dir.iterdir()) == []


def test_forecast_download_failure_propagates(manager, forecast_url):
    for f in forecast_url.iterdir():
        f.unlink()
    with pytest.raises(OSError):
        manager.run_computation_for_single_station(make_station())


def test_upload_failure_does_not_set_checkpoint(manager, connectors, checkpoint_cache, tmp_dir, fake_metro):
    def fail(measures):
        raise RuntimeError("ODH down")
    connectors.road_weather_forecast.post_measures = fail
    station = make_station()

    with pytest.raises(RuntimeError, match="ODH down"):
        manager.run_computation_for_single_station(station)

    assert _checkpoint(checkpoint_cache, station) is None
    assert list(tmp_dir.iterdir()) == []


def test_station_without_wrf_code_is_not_computed(manager, fake_metro):
    assert manager.run_computation_for_single_station(make_station(wrf_code=None)) == 0
    assert fake_metro.calls == []


def test_station_list_comes_from_observation_connector(connectors):
    connectors.road_weather_observation.stations = [make_station()]
    manager = RoadWeatherManager(connectors, Provenance(None, "test", "test", "0"))
    assert [s.code for s in manager.get_station_list()] == [RW_STATION_CODE]



def test_observations_not_suitable_for_metro_are_skipped_and_retried(checkpoint_cache, fake_metro, tmp_dir):
    measures = [m for m in load_observation_measures(make_station()) if m.data_type.name != "temp_suolo"]
    connectors = FakeConnectorCollector(FakeConnector(measures=measures))
    manager = RoadWeatherManager(connectors, Provenance(None, "test", "test", "0"), checkpoint_cache)
    station = make_station()

    assert manager.run_computation_for_single_station(station) == 0

    assert fake_metro.calls == []
    assert connectors.road_weather_forecast.posted_measures == []
    assert _checkpoint(checkpoint_cache, station) is None
