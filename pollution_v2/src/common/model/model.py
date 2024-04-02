# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from abc import ABC, abstractmethod
from typing import List

from common.data_model import MeasureCollection
from common.data_model.entry import GenericEntry


class GenericModel(ABC):
    """
    Abstract class representing a model able to compute data.
    """

    @abstractmethod
    def compute_data(self, traffic_measure_collection: MeasureCollection) -> List[GenericEntry]:
        """
        Compute the output measure given the available traffic measures

        :param traffic_measure_collection: A collection which contain all the available traffic measures
        :return: A list of the new computed pollution measures
        """
        pass
