# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import pytest

from common.data_model import Provenance, Station
from common.data_model.common import DataType
from common.data_model.road_weather import RoadWeatherObservationMeasure

DATA_DIR = Path(__file__).parent / "data" / "road_weather"

# ODH code and WRF code of the station the fixtures have been recorded for
RW_STATION_CODE = "2021"
RW_WRF_CODE = "101"
# start of the recorded forecast (UTC)
RW_FORECAST_START = datetime(2024, 8, 27, 21, 0, tzinfo=timezone.utc)


def make_station(code: str = RW_STATION_CODE, wrf_code: str = RW_WRF_CODE) -> Station:
    return Station(code=code, wrf_code=wrf_code, meteo_station_code=None, active=True, available=True,
                   coordinates={"x": 11.4, "y": 46.9, "srid": 4326}, metadata={}, name=f"RWIS {code}",
                   station_type="RWISstation", origin="A22")


def load_observation_measures(station: Station) -> List[RoadWeatherObservationMeasure]:
    """
    Builds the ODH measures (one per variable and time) out of the recorded observations.
    Times in the CSV are UTC, as ODH returns them.
    """
    provenance = Provenance("prov-1", "test", "test", "0")
    measures = []
    with open(DATA_DIR / "raw-observation_101.csv", newline="") as f:
        for row in csv.DictReader(f):
            valid_time = datetime.strptime(row["time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            for name in ("prec_qta", "stato_meteo", "temp_aria", "temp_rugiada", "temp_suolo", "vento_vel"):
                measures.append(RoadWeatherObservationMeasure(
                    station=station, data_type=DataType(name, None, None, None, None), provenance=provenance,
                    period=1, transaction_time=None, valid_time=valid_time, value=float(row[name])))
            # these ones are not in the recorded file, but are always returned by ODH
            for name in ("umidita_rel", "vento_dir"):
                measures.append(RoadWeatherObservationMeasure(
                    station=station, data_type=DataType(name, None, None, None, None), provenance=provenance,
                    period=1, transaction_time=None, valid_time=valid_time, value=50.0))
    return measures


def recorded_roadcast() -> bytes:
    """The roadcast recorded from METRo."""
    return (DATA_DIR / "roadcast_101.xml").read_bytes()


class FakeConnector:
    """Stands for ODHBaseConnector: serves observation measures and records what is posted."""

    def __init__(self, measures=None, stations=None):
        self.measures = measures or []
        self.stations = stations or []
        self.posted_measures = []
        self.posted_data_types = []
        self.posted_provenances = []
        self.requested_intervals = []

    def get_station_list(self):
        return self.stations

    def get_measures(self, from_date, to_date, station=None, **kwargs):
        self.requested_intervals.append((from_date, to_date))
        return [m for m in self.measures if from_date <= m.valid_time <= to_date
                and (station is None or m.station.code == station.code)]

    def post_provenance(self, provenance):
        self.posted_provenances.append(provenance)
        return "prov-new"

    def post_data_types(self, data_types, provenance):
        self.posted_data_types.append(data_types)

    def post_measures(self, measures):
        self.posted_measures.extend(measures)


class FakeConnectorCollector:
    def __init__(self, observations: FakeConnector = None):
        self.road_weather_observation = observations or FakeConnector()
        self.road_weather_forecast = FakeConnector()
        self.road_weather_conf_level = FakeConnector()


FAKE_METRO_SCRIPT = """
import json, shutil, sys
args = sys.argv[1:]
option = lambda name: args[args.index(name) + 1]
with open({calls!r}, "a") as f:
    f.write(json.dumps(args) + "\\n")
if {fail!r}:
    sys.exit("METRo failed")
shutil.copy({roadcast!r}, option("--output-roadcast"))
"""


class FakeMetro:
    """
    Stands for the METRo executable: it copies the recorded roadcast to the requested output file (or fails), and
    keeps the arguments METRo has been called with in `calls`.
    """

    def __init__(self, path: Path, fail: bool = False):
        self._calls_file = Path(str(path) + ".calls")
        path.write_text(FAKE_METRO_SCRIPT.format(fail=fail, roadcast=str(DATA_DIR / "roadcast_101.xml"),
                                                 calls=str(self._calls_file)))
        self.path = str(path)

    @property
    def calls(self) -> list:
        if not self._calls_file.exists():
            return []
        return [json.loads(line) for line in self._calls_file.read_text().splitlines()]


@pytest.fixture
def fake_metro(monkeypatch, tmp_path):
    metro = FakeMetro(tmp_path / "fake_metro.py")
    monkeypatch.setattr("road_weather.model.road_weather_model.METRO_PYTHON", sys.executable)
    monkeypatch.setattr("road_weather.model.road_weather_model.METRO_BIN", metro.path)
    return metro


@pytest.fixture
def failing_metro(monkeypatch, tmp_path):
    metro = FakeMetro(tmp_path / "failing_metro.py", fail=True)
    monkeypatch.setattr("road_weather.model.road_weather_model.METRO_PYTHON", sys.executable)
    monkeypatch.setattr("road_weather.model.road_weather_model.METRO_BIN", metro.path)
    return metro


@pytest.fixture
def tmp_dir(tmp_path, monkeypatch) -> Path:
    """Redirects the temporary files of the road weather job, so that tests can check they are cleaned up."""
    work = tmp_path / "tmp"
    work.mkdir()
    monkeypatch.setattr("road_weather.model.road_weather_model.TMP_DIR", str(work))
    monkeypatch.setattr("road_weather.manager.road_weather.TMP_DIR", str(work))
    return work


@pytest.fixture
def forecast_url(tmp_path, monkeypatch) -> Path:
    """Serves the recorded forecast through a file:// URL instead of CISMA."""
    served = tmp_path / "wrf"
    served.mkdir()
    (served / f"{RW_WRF_CODE}.xml").write_bytes((DATA_DIR / "forecast_101.xml").read_bytes())
    monkeypatch.setattr("road_weather.manager.road_weather.FORECAST_URL_TEMPLATE", served.as_uri() + "/{}.xml")
    return served
