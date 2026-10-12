# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import subprocess
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree

import pandas as pd
import pytest

from common.data_model import RoadWeatherObservationMeasureCollection
from common.data_model.roadcast import RoadCastClass, RoadCastTypeClass
from road_weather.manager._forecast import Forecast
from road_weather.model import road_weather_model
from road_weather.model.road_weather_model import RoadWeatherModel, RoadConditions

from tests.conftest import (DATA_DIR, RW_FORECAST_START, RW_STATION_CODE, RW_WRF_CODE, load_observation_measures,
                            make_station, recorded_roadcast)


# --- roadcast parsing -------------------------------------------------------------------------------------------

def test_parse_roadcast_generates_one_entry_per_forecast_step():
    entries = RoadWeatherModel.parse_roadcast(recorded_roadcast(), make_station())

    assert len(entries) == road_weather_model.ROAD_WEATHER_NUM_FORECASTS
    assert [e.entry_class for e in entries] == [
        RoadCastTypeClass.get_by_suffix(str(i * road_weather_model.ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS))
        for i in range(1, road_weather_model.ROAD_WEATHER_NUM_FORECASTS + 1)]
    assert all(e.roadcast_class == RoadCastClass.ROADCAST for e in entries)
    assert all(e.station.code == RW_STATION_CODE for e in entries)


def test_parse_roadcast_times_are_utc_and_hourly_after_the_first_roadcast():
    entries = RoadWeatherModel.parse_roadcast(recorded_roadcast(), make_station())

    # the first prediction of the recorded roadcast is 2024-08-27T21:20Z, in UTC. It must not be relabelled with
    # the local timezone, which would shift every forecast by one or two hours
    first = entries[0]
    assert first.valid_time == datetime(2024, 8, 27, 22, 20, tzinfo=timezone.utc)
    assert first.valid_time.utcoffset() == timedelta(0)
    assert [b.valid_time - a.valid_time for a, b in zip(entries, entries[1:])] == [timedelta(hours=1)] * 44


def test_parse_roadcast_maps_road_conditions():
    xml = recorded_roadcast().decode()
    # make the first needed prediction (22:20) an icy one
    first = xml.index("<roadcast-time>2024-08-27T22:20Z</roadcast-time>")
    rc = xml.index("<rc>", first)
    xml = xml[:rc] + "<rc>3</rc>" + xml[rc + len("<rc>1</rc>"):]

    entries = RoadWeatherModel.parse_roadcast(xml.encode(), make_station())

    assert entries[0].entry_value == RoadConditions.RC3.value == "Ice / snow on the road"
    assert {e.entry_value for e in entries[1:]} <= {c.value for c in RoadConditions}


def test_parse_roadcast_period_is_the_one_of_the_forecast_connector():
    entries = RoadWeatherModel.parse_roadcast(recorded_roadcast(), make_station())
    assert {e.period for e in entries} == {1}


def test_parse_roadcast_skips_steps_beyond_the_horizon(monkeypatch):
    monkeypatch.setattr(road_weather_model, "ROAD_WEATHER_NUM_FORECASTS", 200)
    monkeypatch.setattr(road_weather_model, "ROAD_WEATHER_MINUTES_BETWEEN_FORECASTS", 30)
    entries = RoadWeatherModel.parse_roadcast(recorded_roadcast(), make_station())
    # the recorded roadcast ends on 2024-08-30T00:00, the forecast steps further than that carry no value and are skipped
    assert entries
    assert max(e.valid_time for e in entries) <= datetime(2024, 8, 30, 0, 0, tzinfo=timezone.utc)
    assert all(e.entry_value is not None for e in entries)


def test_parse_roadcast_ignores_steps_without_data_type(monkeypatch):
    # forecast-2940 and following are not defined as data types
    monkeypatch.setattr(road_weather_model, "ROAD_WEATHER_NUM_FORECASTS", 60)
    entries = RoadWeatherModel.parse_roadcast(recorded_roadcast(), make_station())
    assert all(e.entry_class is not None for e in entries)
    assert len(entries) == 48


def test_parse_roadcast_without_predictions_fails():
    xml = b"<roadcast><header/><prediction-list/></roadcast>"
    with pytest.raises(ValueError):
        RoadWeatherModel.parse_roadcast(xml, make_station())


def test_parse_roadcast_accepts_response_with_xml_declaration():
    # this is how the web service serializes the roadcast
    xml = b"<?xml version='1.0' encoding='utf8'?>\n" + recorded_roadcast().split(b"?>", 1)[-1]
    entries = RoadWeatherModel.parse_roadcast(xml, make_station())
    assert entries


# --- observations -----------------------------------------------------------------------------------------------

def test_observation_entries_tolerate_missing_optional_measures():
    station = make_station()
    measures = [m for m in load_observation_measures(station)
                if m.data_type.name in ("temp_aria", "vento_vel", "umidita_rel", "vento_dir")]
    entries = RoadWeatherObservationMeasureCollection(measures=measures).get_entries()

    assert entries
    assert all(e.temp_suolo is None and e.temp_rugiada is None and e.prec_qta is None and e.stato_meteo is None
               for e in entries)


def test_observation_entries_tolerate_missing_wind_and_humidity():
    station = make_station()
    measures = [m for m in load_observation_measures(station) if m.data_type.name == "temp_aria"]
    entries = RoadWeatherObservationMeasureCollection(measures=measures).get_entries()
    assert entries and all(e.vento_vel is None and e.umidita_rel is None and e.vento_dir is None for e in entries)


def test_observations_dataframe_is_utc_sorted_and_complete():
    station = make_station()
    measures = load_observation_measures(station)
    # reverse order, different timezone and a missing variable
    measures = [m for m in reversed(measures) if not (m.data_type.name == "temp_suolo"
                                                       and m.valid_time.minute == 11)]
    for m in measures:
        m.valid_time = m.valid_time.astimezone(timezone(timedelta(hours=2)))

    df = RoadWeatherModel._get_observations_dataframe(RoadWeatherObservationMeasureCollection(measures))

    assert list(df.columns) == ["time", "prec_qta", "stato_meteo", "temp_aria", "temp_rugiada", "temp_suolo",
                                "vento_vel"]
    assert df["time"].is_monotonic_increasing
    assert df["time"].iloc[0] == pd.Timestamp("2024-08-27 05:11:00")  # naive UTC, not +02:00
    assert df["time"].iloc[-1] == pd.Timestamp("2024-08-28 04:46:00")
    assert df["temp_suolo"].iloc[0] == 0 and df["temp_suolo"].iloc[1] != 0  # missing values are no data (0)


# --- forecast ---------------------------------------------------------------------------------------------------

def test_forecast_start_and_hourly_interpolation():
    forecast = Forecast(RW_WRF_CODE)
    forecast.load_xml((DATA_DIR / "forecast_101.xml").read_bytes())
    assert forecast.start == "2024-08-27T21:00"

    forecast.interpolate_hourly()
    times = [datetime.strptime(p.find("forecast-time").text, "%Y-%m-%dT%H:%M:%SZ")
             for p in forecast.root.find(".//prediction-list")]
    assert times == sorted(times)
    assert {b - a for a, b in zip(times, times[1:])} == {timedelta(hours=1)}


def test_forecast_interpolation_fills_gaps():
    xml = """<forecast><header/><prediction-list>
      <prediction><forecast-time>2024-08-27T21:00:00Z</forecast-time><at>10.0</at><cc>0</cc></prediction>
      <prediction><forecast-time>2024-08-28T00:00:00Z</forecast-time><at>13.0</at><cc>3</cc></prediction>
    </prediction-list></forecast>"""
    forecast = Forecast(RW_WRF_CODE)
    forecast.load_xml(xml)
    forecast.interpolate_hourly()

    predictions = list(forecast.root.find(".//prediction-list"))
    assert [p.find("forecast-time").text for p in predictions] == [
        "2024-08-27T21:00:00Z", "2024-08-27T22:00:00Z", "2024-08-27T23:00:00Z", "2024-08-28T00:00:00Z"]
    assert [p.find("at").text for p in predictions] == ["10.0", "11.0", "12.0", "13.0"]
    assert [p.find("cc").text for p in predictions] == ["0", "1", "2", "3"]


def test_forecast_negative_radiation_is_zeroed():
    xml = """<forecast><header/><prediction-list>
      <prediction><forecast-time>2024-08-27T21:00:00Z</forecast-time><ir>-5.0</ir><sf>-0.1</sf><at>-3.0</at></prediction>
    </prediction-list></forecast>"""
    forecast = Forecast(RW_WRF_CODE)
    forecast.load_xml(xml)
    forecast.negative_radiation_filter()
    prediction = forecast.root.find(".//prediction")
    assert prediction.find("ir").text == "0.0" and prediction.find("sf").text == "0.0"
    assert prediction.find("at").text == "-3.0"  # temperatures can be negative


# --- compute_data with METRo -------------------------------------------------------------------------------------

def _observations():
    return RoadWeatherObservationMeasureCollection(load_observation_measures(make_station()))


def test_compute_data_runs_metro_with_inputs_and_returns_entries(fake_metro, tmp_dir):
    entries = RoadWeatherModel().compute_data(_observations(), str(DATA_DIR / "forecast_101.xml"),
                                              RW_FORECAST_START, make_station())

    (args,) = fake_metro.calls
    option = lambda name: args[args.index(name) + 1]
    assert option("--input-forecast") == str(DATA_DIR / "forecast_101.xml")
    assert option("--input-station").endswith(f"parameters_{RW_WRF_CODE}.xml")
    assert os.path.exists(option("--input-station"))
    assert option("--roadcast-start-date") == "2024-08-27T21:00"

    assert len(entries) == road_weather_model.ROAD_WEATHER_NUM_FORECASTS
    # the confidence level is 0 if the observations lack data (the recorded ones do), 1 otherwise
    assert {e.conf_level for e in entries} == {"0"}
    assert list(tmp_dir.iterdir()) == []  # inputs and outputs of METRo removed


def test_compute_data_sends_valid_observations_xml_to_metro(monkeypatch, fake_metro, tmp_dir):
    sent = {}
    original = road_weather_model.RoadWeatherModel._run_metro

    def spy(station, forecast, observation, *args):
        sent["xml"] = open(observation).read()
        return original(station, forecast, observation, *args)

    monkeypatch.setattr(road_weather_model.RoadWeatherModel, "_run_metro", staticmethod(spy))
    RoadWeatherModel().compute_data(_observations(), str(DATA_DIR / "forecast_101.xml"), RW_FORECAST_START,
                                    make_station())

    root = ElementTree.fromstring(sent["xml"])
    times = [m.findtext("observation-time") for m in root.findall(".//measure")]
    assert times[0] == "2024-08-27T05:10:00Z" and times[-1] == "2024-08-28T04:45:00Z"  # 5 minutes, UTC
    assert [c.tag for c in root.find("./measure-list/measure")] == [
        "observation-time", "at", "td", "st", "ws", "pi", "sc", "sst"]


def test_compute_data_fails_if_metro_fails_and_cleans_up(failing_metro, tmp_dir):
    with pytest.raises(subprocess.CalledProcessError):
        RoadWeatherModel().compute_data(_observations(), str(DATA_DIR / "forecast_101.xml"), RW_FORECAST_START,
                                        make_station())
    assert list(tmp_dir.iterdir()) == []


def test_compute_data_rejects_observations_without_soil_temperature(fake_metro, tmp_dir):
    measures = [m for m in load_observation_measures(make_station()) if m.data_type.name != "temp_suolo"]
    # METRo needs at least two valid soil temperatures
    with pytest.raises(ValueError):
        RoadWeatherModel().compute_data(RoadWeatherObservationMeasureCollection(measures),
                                        str(DATA_DIR / "forecast_101.xml"), RW_FORECAST_START, make_station())
    assert fake_metro.calls == []
    assert list(tmp_dir.iterdir()) == []
