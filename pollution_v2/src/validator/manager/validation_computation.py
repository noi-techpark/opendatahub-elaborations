# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging

from common.connector.common import ODHBaseConnector
from common.manager.traffic_station import TrafficStationManager
from validator.model.validatation_model import ValidationModel

logger = logging.getLogger("validator.manager.validation_computation")


class ValidationComputationManager(TrafficStationManager):

    def _get_model(self) -> ValidationModel:
        return ValidationModel()

    def _get_main_collector(self) -> ODHBaseConnector:
        return self._connector_collector.validation

    def _get_latest_date_collector(self) -> ODHBaseConnector:
        return self._connector_collector.traffic
