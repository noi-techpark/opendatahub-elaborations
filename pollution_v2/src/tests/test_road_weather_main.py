# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path

import pytest

from road_weather.main import load_config, process_stations
from tests.conftest import make_station

CONFIG_DIR = Path(__file__).parents[1] / "config"


class StubManager:
    def __init__(self, results):
        self.results = results
        self.processed = []

    def run_computation_for_single_station(self, station):
        self.processed.append((station.code, station.wrf_code))
        result = self.results[station.code]
        if isinstance(result, Exception):
            raise result
        return result


def test_shipped_config_is_valid():
    whitelist, mapping = load_config(str(CONFIG_DIR / "road_weather.yaml"))
    assert whitelist and set(whitelist) <= set(mapping)
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in mapping.items())
    assert len(set(mapping.values())) == len(mapping)  # a WRF station is used once

    # every station of the config has METRo parameters
    parameters = Path(__file__).parents[2] / "weather" / "data" / "parameters"
    if parameters.exists():
        for wrf_code in mapping.values():
            assert (parameters / f"parameters_{wrf_code}.xml").exists(), wrf_code


def test_load_config_without_whitelist_and_with_empty_whitelist(tmp_path):
    f = tmp_path / "c.yaml"
    f.write_text("mappings:\n  1: '101'\n")
    assert load_config(str(f)) == ([], {"1": "101"})
    f.write_text("whitelist:\nmappings:\n  1: '101'\n")
    assert load_config(str(f)) == ([], {"1": "101"})


def test_load_config_requires_mappings(tmp_path):
    f = tmp_path / "c.yaml"
    f.write_text("whitelist: [1]\n")
    with pytest.raises(ValueError):
        load_config(str(f))


def test_process_stations_isolates_failures_and_counts():
    stations = [make_station(code=c) for c in ("1", "2", "3", "4", "5")]
    manager = StubManager({"1": 45, "2": RuntimeError("metro down"), "3": 0, "5": 10})

    summary = process_stations(manager, stations, {"1": "101", "2": "102", "3": "103", "5": "105"})

    assert (summary.ok, summary.skipped, summary.failed, summary.entries) == (2, 2, 1, 55)
    # station 4 has no mapping and is not computed; station 5 is processed even after 2 failed
    assert manager.processed == [("1", "101"), ("2", "102"), ("3", "103"), ("5", "105")]
