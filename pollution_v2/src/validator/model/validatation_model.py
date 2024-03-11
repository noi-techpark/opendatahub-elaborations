# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import datetime
import json
import logging
from typing import List, Iterable, Dict

import pandas as pd

from common.data_model.common import VehicleClass
from common.data_model.pollution import PollutionEntry, PollutantClass
from common.data_model import TrafficMeasureCollection, TrafficEntry, TrafficSensorStation
from common.data_model.validation import ValidationEntry
from common.model.model import GenericModel
from pollution_connector.model.CopertEmissions import copert_emissions

logger = logging.getLogger("pollution_v2.validator.model.validation_model")


class ValidationModel(GenericModel):

    def __init__(self):
        pass

    def compute_data(self, traffic_measure_collection: TrafficMeasureCollection) -> List[ValidationEntry]:
        """
        Compute the validation given the available traffic measures
        :param traffic_measure_collection: A collection which contain all the available traffic measures
        :return: A list of the new computed validation measures
        """
        logger.warning("missing implementation!")
        return []
