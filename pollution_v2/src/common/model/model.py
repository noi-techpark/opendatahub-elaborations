# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from abc import ABC, abstractmethod
from typing import Generic, List

from common.data_model import MeasureCollection
from common.data_model.common import MeasureCollectionType
from common.data_model.entry import GenericEntry


class GenericModel(ABC, Generic[MeasureCollectionType]):

    @abstractmethod
    def compute_data(self, traffic_measure_collection: MeasureCollection) -> List[GenericEntry]:
        pass
