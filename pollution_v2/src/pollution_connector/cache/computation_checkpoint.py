# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Union

import redis

from pollution_connector.cache.common import CacheData, RedisCache
from common.data_model.common import Station


@dataclass
class ComputationCheckpoint(CacheData):

    station_code: str
    checkpoint_dt: datetime

    @staticmethod
    def get_id_for_station(station: Union[Station, str]) -> str:
        base_key = "ComputationCheckpoint"
        if isinstance(station, str):
            return f"{base_key}-{station}"
        elif isinstance(station, Station):
            return f"{base_key}-{station.code}"
        else:
            raise TypeError(f"Unable to handle an object of type [{type(station)}]")

    def unique_id(self) -> str:
        return self.get_id_for_station(self.station_code)

    def to_repr(self) -> dict:
        return {
            "stationCode": self.station_code,
            "checkpointDT": self.checkpoint_dt.isoformat()
        }

    @staticmethod
    def from_repr(raw_data: dict) -> CacheData:
        return ComputationCheckpoint(
            station_code=raw_data["stationCode"],
            checkpoint_dt=datetime.fromisoformat(raw_data["checkpointDT"])
        )


class ComputationCheckpointCache(RedisCache[ComputationCheckpoint]):

    def __init__(self, r: redis.Redis) -> None:
        super().__init__(r, ComputationCheckpoint)
