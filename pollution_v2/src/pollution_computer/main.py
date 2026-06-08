# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import sys

import sentry_sdk

from common.cache.computation_checkpoint import ComputationCheckpointCache
from common.connector.collector import ConnectorCollector
from common.data_model.common import Provenance
from common.logging import setup_logging
from common.settings import (
    COMPUTATION_CHECKPOINT_CACHE_PATH,
    DEFAULT_TIMEZONE,
    ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION,
    ODH_MINIMUM_STARTING_DATE,
    PROVENANCE_ID,
    PROVENANCE_LINEAGE,
    PROVENANCE_NAME_POLL_ELABORATION,
    PROVENANCE_VERSION,
    SENTRY_SAMPLE_RATE,
    get_previous_midnight,
)
from pollution_computer.manager.pollution_computation import PollutionComputationManager

setup_logging("pollution-computer")
logger = logging.getLogger("pollution_v2.pollution_computer.main")

sentry_sdk.init(traces_sample_rate=SENTRY_SAMPLE_RATE)


def main() -> None:
    checkpoint_cache = None
    if COMPUTATION_CHECKPOINT_CACHE_PATH:
        logger.info(f"Checkpoint cache enabled at {COMPUTATION_CHECKPOINT_CACHE_PATH}")
        checkpoint_cache = ComputationCheckpointCache(COMPUTATION_CHECKPOINT_CACHE_PATH)

    connector_collector = ConnectorCollector.build_from_env()
    provenance = Provenance(PROVENANCE_ID, PROVENANCE_LINEAGE, PROVENANCE_NAME_POLL_ELABORATION, PROVENANCE_VERSION)
    manager = PollutionComputationManager(connector_collector, provenance, checkpoint_cache)

    min_from_date = ODH_MINIMUM_STARTING_DATE
    # pollution computation runs up to previous midnight to stay in sync with the validation window
    max_to_date = DEFAULT_TIMEZONE.localize(get_previous_midnight())

    stations = manager.get_station_list()
    stations = [s for s in stations if s.km > 0]
    stations = [s for s in stations if s.sensor_type in ("induction_loop", "camera")]
    stations = [s for s in stations if s.origin != "FAMAS-traffic"]
    logger.info(f"Processing {len(stations)} stations")

    for station in stations:
        logger.info(f"Processing station {station.code}")
        try:
            manager.run_computation(
                [station], min_from_date, max_to_date,
                ODH_COMPUTATION_BATCH_SIZE_POLL_ELABORATION, keep_looking_for_input_data=False
            )
        except Exception:
            logger.exception(f"Failed to process station {station.code}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Unhandled error in pollution-computer job")
        sys.exit(1)
