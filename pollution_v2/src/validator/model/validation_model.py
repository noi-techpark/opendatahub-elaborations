# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from typing import List

from common.data_model import TrafficMeasureCollection
from common.data_model.validation import ValidationEntry
from common.model.model import GenericModel

logger = logging.getLogger("pollution_v2.validator.model.validation_model")


class ValidationModel(GenericModel):
    """
    The model for computing validation data.
    """

    def __init__(self):
        pass

    def compute_data(self, traffic_measure_collection: TrafficMeasureCollection) -> List[ValidationEntry]:
        """
        Compute the validation given the available traffic measures

        :param traffic_measure_collection: A collection which contain all the available traffic measures
        :return: A list of the new computed validation measures
        """
        logger.warning("missing implementation!")
        # TODO implement
        return []
