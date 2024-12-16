# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from common.cache.common import TrafficManagerClass
from common.cache.computation_checkpoint import ComputationCheckpointCache
from common.connector.collector import ConnectorCollector
from common.connector.common import ODHBaseConnector
from common.data_model import Provenance, DataType, MeasureCollection, PollutionMeasureCollection, \
    PollutionDispersalMeasure, TrafficSensorStation, PollutionMeasure, PollutantClass
from common.data_model.entry import GenericEntry
from common.data_model.pollution_dispersal import PollutionDispersalEntry
from common.data_model.weather import WeatherMeasureCollection
from common.manager.station import StationManager
from common.manager.traffic_station import TrafficStationManager
from common.settings import DEFAULT_TIMEZONE, DAG_POLLUTION_DISPERSAL_TRIGGER_DAG_HOURS_SPAN
from pollution_dispersal.model.pollution_dispersal_model import PollutionDispersalModel

logger = logging.getLogger("pollution_v2.pollution_dispersal.manager.pollution_dispersal")


class PollutionDispersalManager(StationManager):
    """
    Manager in charge of executing pollution computation.
    """

    def __init__(self, connector_collector: ConnectorCollector, provenance: Provenance,
                 checkpoint_cache: Optional[ComputationCheckpointCache] = None) -> None:
        super().__init__(connector_collector, provenance, checkpoint_cache)
        self.station_list_connector = self.get_input_connector()

    def _get_manager_code(self) -> str:
        return TrafficManagerClass.DISPERSAL.name

    def get_input_connector(self) -> ODHBaseConnector:
        return self._connector_collector.pollution

    def get_input_additional_connector(self) -> ODHBaseConnector:
        return self._connector_collector.weather

    def get_output_connector(self) -> ODHBaseConnector:
        return self._connector_collector.pollution_dispersal

    def _get_data_types(self) -> List[DataType]:
        return PollutionDispersalMeasure.get_data_types()

    def _build_from_entries(self, input_entries: List[PollutionDispersalEntry]) -> MeasureCollection:
        # TODO: implement when needed
        pass

    def _download_pollution_data(self,
                                   from_date: datetime,
                                   to_date: datetime,
                                   ) -> PollutionMeasureCollection:
        """
        Download pollution data measures in the given interval.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting PollutionMeasureCollection containing the pollution data.
        """

        connector = self.get_input_connector()
        logger.info(f"Downloading pollution data from [{from_date}] to [{to_date}]")
        nox_pollutants = PollutionMeasure.get_data_types([PollutantClass.NOx])
        return PollutionMeasureCollection(
            measures=connector.get_measures(from_date=from_date, to_date=to_date, measure_types=list(map(lambda x: x.name, nox_pollutants)))
        )

    def _download_weather_data(self,
                                   from_date: datetime,
                                   to_date: datetime,
                                   ) -> WeatherMeasureCollection:
        """
        Download weather data measures in the given interval.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting WeatherMeasureCollection containing the weather data.
        """

        connector = self.get_input_additional_connector()
        logger.info(f"Downloading weather data from [{from_date}] to [{to_date}]")
        return WeatherMeasureCollection(
            measures=connector.get_measures(from_date=from_date, to_date=to_date)
        )

    def _download_data_and_compute(self, stations: List[TrafficSensorStation]) -> List[GenericEntry]:

        if len(stations) < 1:
            logger.error(f"Cannot compute pollution dispersal on empty station list ({len(stations)} passed)")
            return []

        start_date = datetime.now()  # TODO: localize?
        start_date = datetime(2020, 1, 1, 0)  # TODO: remove
        to_date = start_date + timedelta(hours=DAG_POLLUTION_DISPERSAL_TRIGGER_DAG_HOURS_SPAN)
        logger.info(f"Computing pollution dispersal from {start_date} to {to_date} for stations {stations}")

        pollution_data = None
        weather_data = None
        try:
            pollution_data = self._download_pollution_data(start_date, to_date)
            weather_data = self._download_weather_data(start_date, to_date)
        except Exception as e:
            logger.exception(
                f"Unable to download pollution and weather data for stations {stations}",
                exc_info=e)

        if pollution_data and weather_data:
            logger.info(f"Length of pollution data: {len(pollution_data.measures)}")
            logger.info(f"Length of weather data: {len(weather_data.measures)}")

            logger.info("Filtering pollution data by station ids")
            pollution_data = PollutionMeasureCollection(list(filter(lambda x: x.station.code in [station.code for station in stations], pollution_data.measures)))
            logger.info(f"Length of pollution data after filtering: {len(pollution_data.measures)}")

            logger.info("Filtering weather data by station ids")
            weather_data = WeatherMeasureCollection(list(filter(lambda x: x.station.code in [station.meteo_station_code for station in stations], weather_data.measures)))
            logger.info(f"Length of weather data after filtering: {len(weather_data.measures)}")

            model = PollutionDispersalModel()
            return model.compute_data(pollution_data, weather_data, start_date, stations)

        return []

    def run_computation_for_multiple_stations(self, stations: List[TrafficSensorStation]) -> None:
        """
        Run the computation for multiple stations.

        :param stations: The list of stations to compute.
        """
        entries = self._download_data_and_compute(stations)
        logger.info(f"Computed {len(entries)} pollution dispersal entries")
        # self._upload_data(entries)  # TODO: restore
