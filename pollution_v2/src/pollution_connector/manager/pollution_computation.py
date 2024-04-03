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
from common.data_model.validation import ValidationMeasureCollection
from common.manager.traffic_station import TrafficStationManager
from common.data_model.common import DataType, MeasureCollection
from common.data_model.pollution import PollutionMeasure, PollutionMeasureCollection, PollutionEntry
from common.settings import DEFAULT_TIMEZONE
from pollution_connector.model.pollution_computation_model import PollutionComputationModel

logger = logging.getLogger("pollution_v2.pollution_connector.manager.pollution_computation")


class PollutionComputationManager(TrafficStationManager):
    """
    Manager in charge of executing pollution computation.
    """

    def _get_manager_code(self) -> str:
        return TrafficManagerClass.POLLUTION.name

    def get_output_connector(self) -> ODHBaseConnector:
        return self._connector_collector.pollution

    def get_input_connector(self) -> ODHBaseConnector:
        # on v1 it would have been self._connector_collector.traffic
        return self._connector_collector.validation

    def _download_validation_data(self,
                                  from_date: datetime,
                                  to_date: datetime,
                                  traffic_station: TrafficSensorStation
                                  ) -> ValidationMeasureCollection:
        """
        Download validation data measures in the given interval.

        :param from_date: Measures before this date are discarded if there isn't any latest measure available.
        :param to_date: Measures after this date are discarded.
        :return: The resulting ValidationMeasureCollection containing the validated traffic data.
        """

        return ValidationMeasureCollection(
            measures=self._connector_collector.validation.get_measures(from_date=from_date, to_date=to_date,
                                                                       station=traffic_station))

    def _download_data_and_compute(self, start_date: datetime, to_date: datetime,
                                   traffic_station: TrafficSensorStation) -> List[GenericEntry]:

        validation_data = []
        traffic_data = []
        try:
            validation_data = self._download_validation_data(start_date, to_date, traffic_station)
            traffic_data = self._download_traffic_data(start_date, to_date, traffic_station)
        except Exception as e:
            logger.exception(
                f"Unable to download validation and traffic data for station [{traffic_station.code}] "
                f"in the interval [{start_date.isoformat()}] - [{to_date.isoformat()}]",
                exc_info=e)

        if validation_data and traffic_data:
            model = PollutionComputationModel()
            return model.compute_data(validation_data, TrafficMeasureCollection(traffic_data), traffic_station)

        return []

    def _get_data_types(self) -> List[DataType]:
        return PollutionMeasure.get_data_types()

    def _build_from_entries(self, input_entries: List[PollutionEntry]) -> MeasureCollection:
        return PollutionMeasureCollection.build_from_entries(input_entries, self._provenance)
