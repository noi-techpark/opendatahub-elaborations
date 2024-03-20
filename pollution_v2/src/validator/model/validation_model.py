# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from typing import List

from common.data_model import TrafficMeasureCollection
from common.data_model.history import HistoryMeasureCollection
from common.data_model.validation import ValidationEntry

logger = logging.getLogger("pollution_v2.validator.model.validation_model")


class ValidationModel:
    """
    The model for computing validation data.
    """

    def compute_data(self, history: HistoryMeasureCollection, traffic: TrafficMeasureCollection) -> List[ValidationEntry]:
        """
        Compute the validation given the available traffic measures

        :param history: A collection which contain measures history
        :param traffic: A collection which contain all the available traffic measures
        :return: A list of the new computed validation measures
        """
        logger.warning("missing implementation!")
        # TODO implement
        return []
