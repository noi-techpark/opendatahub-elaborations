# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from typing import List

from common.connector.common import ODHBaseConnector
from common.data_model import DataType
from common.data_model.validation import ValidationEntry, ValidationMeasure, ValidationMeasureCollection
from common.manager.traffic_station import TrafficStationManager, TrafficManagerClass
from validator.model.validatation_model import ValidationModel

logger = logging.getLogger("pollution_v2.validator.manager.validation")


class ValidationManager(TrafficStationManager):

    def _get_type(self) -> TrafficManagerClass:
        return TrafficManagerClass.VALIDATION

    def _get_model(self) -> ValidationModel:
        return ValidationModel()

    def _get_data_collector(self) -> ODHBaseConnector:
        return self._connector_collector.validation

    def _get_date_reference_collector(self) -> ODHBaseConnector:
        return self._connector_collector.traffic

    def _get_data_types(self) -> List[DataType]:
        return ValidationMeasure.get_data_types()

    def _build_from_entries(self, input_entries: List[ValidationEntry]):
        return ValidationMeasureCollection.build_from_validation_entries(input_entries, self._provenance)
