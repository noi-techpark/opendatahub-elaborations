# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from datetime import datetime
from typing import List

from common.cache.common import TrafficManagerClass
from common.connector.common import ODHBaseConnector
from common.data_model import TrafficSensorStation, TrafficMeasureCollection
from common.data_model.entry import GenericEntry
from common.manager.traffic_station import TrafficStationManager
from common.data_model.common import DataType, MeasureCollection
from common.data_model.pollution import PollutionMeasure, PollutionMeasureCollection, PollutionEntry
from pollution_computer.model.pollution_computation_model import PollutionComputationModel

logger = logging.getLogger("pollution_v2.pollution_computer.manager.pollution_computation")


class PollutionComputationManager(TrafficStationManager):
    """
    Manager in charge of executing pollution computation.
    """

    def _get_manager_code(self) -> str:
        return TrafficManagerClass.POLLUTION.name

    def get_output_connector(self) -> ODHBaseConnector:
        return self._connector_collector.pollution

    def get_input_connector(self) -> ODHBaseConnector:
        return self._connector_collector.traffic

    def _download_data_and_compute(self, start_date: datetime, to_date: datetime,
                                   stations: List[TrafficSensorStation]) -> List[GenericEntry]:
        if len(stations) != 1:
            logger.error(f"Cannot compute pollution on more than one station ({len(stations)} passed)")
            return []

        traffic_station = stations[0]
        traffic_data = []
        try:
            traffic_data = self._download_traffic_data(start_date, to_date, [traffic_station])
        except Exception as e:
            logger.exception(
                f"Unable to download traffic data for station [{traffic_station.code}] "
                f"in the interval [{start_date.isoformat()}] - [{to_date.isoformat()}]",
                exc_info=e,
            )

        if traffic_data:
            model = PollutionComputationModel()
            return model.compute_data(TrafficMeasureCollection(traffic_data), traffic_station)

        return []

    def _get_data_types(self) -> List[DataType]:
        return PollutionMeasure.get_data_types()

    def _build_from_entries(self, input_entries: List[PollutionEntry]) -> MeasureCollection:
        return PollutionMeasureCollection.build_from_entries(input_entries, self._provenance)
