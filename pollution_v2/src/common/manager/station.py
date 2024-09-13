from abc import ABC
from typing import List, Optional

from common.cache.computation_checkpoint import ComputationCheckpointCache
from common.connector.collector import ConnectorCollector
from common.data_model import Station, Provenance


class StationManager(ABC):
    """
    Manager in charge of the retrieval of the stations.
    """

    def __init__(self, connector_collector: ConnectorCollector, provenance: Provenance,
                 checkpoint_cache: Optional[ComputationCheckpointCache] = None):
        self._checkpoint_cache = checkpoint_cache
        self._connector_collector = connector_collector
        self._provenance = provenance
        self._create_data_types = True

    def get_station_list(self) -> List[Station]:
        # TODO: implement the retrieval of the stations
        pass
