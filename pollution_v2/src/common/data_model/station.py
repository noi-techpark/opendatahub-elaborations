# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from dataclasses import dataclass

import logging

from common.data_model.common import Station

logger = logging.getLogger("pollution_v2.common.data_model.station")


@dataclass
class TrafficSensorStation(Station):
    """
    Class representing a traffic station
    """

    def split_station_code(self) -> (str, int, int):
        """
        splits the station code using the pattern ID_strada:ID_stazione:ID_corsia and returns a tuple
        with the following structure (ID_strada, ID_stazione, ID_corsia)
        :return:
        """
        splits = self.code.split(":")
        if len(splits) != 3:
            raise ValueError(f"Unable to split [{self.code}] in ID_strada:ID_stazione:ID_corsia")
        return splits[0], int(splits[1]), int(splits[2])

    @property
    def id_strada(self) -> str:
        id_strada, id_stazione, id_corsia = self.split_station_code()
        return id_strada

    @property
    def id_stazione(self) -> int:
        id_strada, id_stazione, id_corsia = self.split_station_code()
        return id_stazione

    @property
    def id_corsia(self) -> int:
        id_strada, id_stazione, id_corsia = self.split_station_code()
        return id_corsia

    @classmethod
    def from_json(cls, dict_data) -> TrafficSensorStation:
        return TrafficSensorStation(
            code=dict_data["code"],
            active=dict_data["active"],
            available=dict_data["available"],
            coordinates=dict_data["coordinates"],
            metadata=dict_data["metadata"],
            name=dict_data["name"],
            station_type=dict_data["station_type"],
            origin=dict_data["origin"]
        )
