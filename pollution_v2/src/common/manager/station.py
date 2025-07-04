# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from common.cache.computation_checkpoint import ComputationCheckpointCache
from common.connector.collector import ConnectorCollector
from common.connector.common import ODHBaseConnector
from common.data_model import Station, Provenance, DataType, MeasureCollection
from common.data_model.entry import GenericEntry

logger = logging.getLogger("pollution_v2.common.manager.station")


class StationManager(ABC):
    """
    Manager in charge of the retrieval of the stations.
    """
    station_list_connector: ODHBaseConnector = None

    def __init__(self, connector_collector: ConnectorCollector, provenance: Provenance,
                 checkpoint_cache: Optional[ComputationCheckpointCache] = None):
        self._checkpoint_cache = checkpoint_cache
        self._connector_collector = connector_collector
        self._provenance = provenance
        self._create_data_types = True

    @abstractmethod
    def get_input_connector(self) -> ODHBaseConnector:
        """
        Returns the collector for retrieving input data for computing and the dates useful to determine processing
        interval for the implementing manager class.
        """
        pass

    @abstractmethod
    def get_output_connector(self) -> ODHBaseConnector:
        """
        Returns the collector of the data in charge of the implementing manager class.
        """
        pass

    @abstractmethod
    def _get_data_types(self) -> List[DataType]:
        """
        Returns the data types specific for the implementing manager class.
        """
        pass

    @abstractmethod
    def _build_from_entries(self, input_entries: List[GenericEntry]) -> MeasureCollection:
        """
        Builds the measure collection given the entries for the implementing manager class.

        :param input_entries: manager specific class entries.
        """
        pass

    def get_station_list(self) -> List[Station]:
        """
        Retrieve the list of stations
        """
        if self.station_list_connector is None:
            raise NotImplementedError("The station_list_connector must be defined")

        return self.station_list_connector.get_station_list()

    def _upload_data(self, input_entries: List[GenericEntry],
                     output_alternative_connector: ODHBaseConnector = None) -> None:
        """
        Upload the input data on ODH.
        If a data is already present it will be not overridden and
        data before the last measures are not accepted by the ODH.

        :param input_entries: The entries to be processed.
        """

        output_connector = self.get_output_connector()
        if output_alternative_connector:
            output_connector = output_alternative_connector

        logger.info(f"Posting provenance {self._provenance}")
        if not self._provenance.provenance_id:
            self._provenance.provenance_id = output_connector.post_provenance(self._provenance)

        logger.info(f"Posting data types {self._get_data_types()}")
        if self._create_data_types:
            output_connector.post_data_types(self._get_data_types(), self._provenance)

        data = self._build_from_entries(input_entries)
        logger.info(f"Posting measures {len(data.measures)}")
        output_connector.post_measures(data.measures)
