# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from datetime import datetime
from typing import Optional, TypeVar

from common.data_model.station import Station


class GenericEntry:
    """
    Superclass representing a basic ODH entry (to be extended in order to manage other fields)
    """
    def __init__(self, station: Station, valid_time: datetime, period: Optional[int]):
        self.station = station
        self.valid_time = valid_time
        self.period = period


GenericEntryType = TypeVar("GenericEntryType", bound=GenericEntry)
