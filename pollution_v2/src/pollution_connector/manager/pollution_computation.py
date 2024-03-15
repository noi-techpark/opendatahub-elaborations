# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from typing import List

from common.cache.common import TrafficManagerClass
from common.connector.common import ODHBaseConnector
from common.manager.traffic_station import TrafficStationManager
from common.data_model.common import DataType, MeasureCollection
from common.data_model.pollution import PollutionMeasure, PollutionMeasureCollection, PollutionEntry
from common.model.model import GenericModel
from pollution_connector.model.pollution_computation_model import PollutionComputationModel

logger = logging.getLogger("pollution_v2.pollution_connector.manager.pollution_computation")


class PollutionComputationManager(TrafficStationManager):
    """
    Manager in charge of executing pollution computation.
    """

    def _get_manager_code(self) -> str:
        return TrafficManagerClass.POLLUTION.name

    def _get_model(self) -> GenericModel:
        return PollutionComputationModel()

    def get_data_collector(self) -> ODHBaseConnector:
        return self._connector_collector.pollution

    def get_date_reference_collector(self) -> ODHBaseConnector:
        # on v1 it would have been self._connector_collector.traffic
        return self._connector_collector.validation

    def _get_data_types(self) -> List[DataType]:
        return PollutionMeasure.get_data_types()

    def _build_from_entries(self, input_entries: List[PollutionEntry]) -> MeasureCollection:
        return PollutionMeasureCollection.build_from_pollution_entries(input_entries, self._provenance)
