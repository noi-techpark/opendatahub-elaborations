# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from typing import List

from common.connector.common import ODHBaseConnector
from common.data_model import DataType
from common.data_model.entry import GenericEntry
from common.manager.traffic_station import TrafficStationManager
from common.data_model.pollution import PollutionMeasure, PollutionMeasureCollection, PollutionEntry
from pollution_connector.model.pollution_computation_model import PollutionComputationModel

logger = logging.getLogger("pollution_connector.manager.pollution_computation")


class PollutionComputationManager(TrafficStationManager):

    def _get_model(self) -> PollutionComputationModel:
        return PollutionComputationModel()

    def _get_main_collector(self) -> ODHBaseConnector:
        return self._connector_collector.pollution

    def _get_latest_date_collector(self) -> ODHBaseConnector:
        return self._connector_collector.validation

    def _get_data_types(self) -> List[DataType]:
        return PollutionMeasure.get_data_types()

    def _build_from_entries(self, input_entries: List[PollutionEntry]):
        return PollutionMeasureCollection.build_from_pollution_entries(input_entries, self._provenance)
