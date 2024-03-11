# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from datetime import datetime
from typing import Optional, TypeVar

from common.data_model.common import VehicleClass
from common.data_model.traffic import TrafficSensorStation


class GenericEntry:

    def __init__(self, station: TrafficSensorStation, valid_time: datetime, vehicle_class: VehicleClass,
                 entry_value: Optional[float], period: Optional[int]):
        self.station = station
        self.valid_time = valid_time
        self.vehicle_class = vehicle_class
        self.entry_value = entry_value
        self.period = period


GenericEntryType = TypeVar("GenericEntryType", bound=GenericEntry)
