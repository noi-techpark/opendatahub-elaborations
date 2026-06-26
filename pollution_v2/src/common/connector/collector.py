# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from common.connector.common import ODHBaseConnector
from common.connector.pollution_dispersal import PollutionDispersalODHConnector
from common.data_model.history import HistoryMeasure, HistoryMeasureType
from common.data_model.pollution import PollutionMeasure
from common.data_model.road_weather import (
    RoadWeatherConfLevelMeasure,
    RoadWeatherConfLevelMeasureType,
    RoadWeatherForecastMeasure,
    RoadWeatherForecastMeasureType,
    RoadWeatherObservationMeasure,
    RoadWeatherObservationMeasureType,
)
from common.data_model.station import Station, TrafficSensorStation
from common.data_model.traffic import TrafficMeasure, TrafficMeasureType
from common.data_model.validation import ValidationMeasure
from common.data_model.weather import WeatherMeasure, WeatherMeasureType
from common.settings import (
    ODH_AUTHENTICATION_URL,
    ODH_BASE_READER_URL,
    ODH_BASE_WRITER_URL,
    ODH_CLIENT_ID,
    ODH_CLIENT_SECRET,
    ODH_GRANT_TYPE,
    ODH_MAX_POST_BATCH_SIZE,
    ODH_PASSWORD,
    ODH_PAGINATION_SIZE,
    ODH_USERNAME,
    PERIOD_10MIN,
    PERIOD_1DAY,
    PERIOD_1HOUR,
    PERIOD_1SEC,
    REQUESTS_MAX_RETRIES,
    REQUESTS_RETRY_SLEEP_TIME,
    REQUESTS_SLEEP_TIME,
    REQUESTS_TIMEOUT,
)


class ConnectorCollector:

    def __init__(self,
                 traffic: ODHBaseConnector,
                 history: ODHBaseConnector,
                 validation: ODHBaseConnector,
                 pollution: ODHBaseConnector,
                 road_weather_observation: ODHBaseConnector,
                 road_weather_forecast: ODHBaseConnector,
                 road_weather_conf_level: ODHBaseConnector,
                 weather: ODHBaseConnector,
                 pollution_dispersal: PollutionDispersalODHConnector) -> None:
        self.traffic = traffic
        self.history = history
        self.validation = validation
        self.pollution = pollution
        self.road_weather_observation = road_weather_observation
        self.road_weather_forecast = road_weather_forecast
        self.road_weather_conf_level = road_weather_conf_level
        self.weather = weather
        self.pollution_dispersal = pollution_dispersal

    @staticmethod
    def build_from_env() -> ConnectorCollector:
        common_kwargs = dict(
            base_reader_url=ODH_BASE_READER_URL,
            base_writer_url=ODH_BASE_WRITER_URL,
            authentication_url=ODH_AUTHENTICATION_URL,
            username=ODH_USERNAME,
            password=ODH_PASSWORD,
            client_id=ODH_CLIENT_ID,
            client_secret=ODH_CLIENT_SECRET,
            grant_type=ODH_GRANT_TYPE,
            pagination_size=ODH_PAGINATION_SIZE,
            max_post_batch_size=ODH_MAX_POST_BATCH_SIZE,
            requests_timeout=REQUESTS_TIMEOUT,
            requests_max_retries=REQUESTS_MAX_RETRIES,
            requests_sleep_time=REQUESTS_SLEEP_TIME,
            requests_retry_sleep_time=REQUESTS_RETRY_SLEEP_TIME,
        )

        return ConnectorCollector(
            traffic=ODHBaseConnector(
                station_type="TrafficSensor",
                measure_types=[mt.value for mt in TrafficMeasureType],
                period=PERIOD_10MIN,
                build_station=TrafficSensorStation.from_odh_repr,
                build_measure=TrafficMeasure.from_odh_repr,
                **common_kwargs,
            ),
            history=ODHBaseConnector(
                station_type="TrafficSensor",
                measure_types=[mt.value for mt in HistoryMeasureType],
                period=PERIOD_1DAY,
                build_station=TrafficSensorStation.from_odh_repr,
                build_measure=HistoryMeasure.from_odh_repr,
                **common_kwargs,
            ),
            validation=ODHBaseConnector(
                station_type="TrafficSensor",
                measure_types=[dt.name for dt in ValidationMeasure.get_data_types()],
                period=PERIOD_10MIN,
                build_station=TrafficSensorStation.from_odh_repr,
                build_measure=ValidationMeasure.from_odh_repr,
                **common_kwargs,
            ),
            pollution=ODHBaseConnector(
                station_type="TrafficSensor",
                measure_types=[dt.name for dt in PollutionMeasure.get_data_types()],
                period=PERIOD_10MIN,
                build_station=TrafficSensorStation.from_odh_repr,
                build_measure=PollutionMeasure.from_odh_repr,
                **common_kwargs,
            ),
            road_weather_observation=ODHBaseConnector(
                station_type="RWISstation",
                measure_types=[mt.value for mt in RoadWeatherObservationMeasureType],
                period=PERIOD_1SEC,
                build_station=Station.from_odh_repr,
                build_measure=RoadWeatherObservationMeasure.from_odh_repr,
                **common_kwargs,
            ),
            road_weather_forecast=ODHBaseConnector(
                station_type="RWISstation",
                measure_types=[mt.value for mt in RoadWeatherForecastMeasureType],
                period=PERIOD_1SEC,
                build_station=Station.from_odh_repr,
                build_measure=RoadWeatherForecastMeasure.from_odh_repr,
                **common_kwargs,
            ),
            road_weather_conf_level=ODHBaseConnector(
                station_type="RWISstation",
                measure_types=[mt.value for mt in RoadWeatherConfLevelMeasureType],
                period=PERIOD_1SEC,
                build_station=Station.from_odh_repr,
                build_measure=RoadWeatherConfLevelMeasure.from_odh_repr,
                **common_kwargs,
            ),
            weather=ODHBaseConnector(
                station_type="MeteoStation",
                measure_types=[mt.value for mt in WeatherMeasureType],
                period=PERIOD_10MIN,
                build_station=Station.from_odh_repr,
                build_measure=WeatherMeasure.from_odh_repr,
                **common_kwargs,
            ),
            pollution_dispersal=PollutionDispersalODHConnector(**common_kwargs),
        )
