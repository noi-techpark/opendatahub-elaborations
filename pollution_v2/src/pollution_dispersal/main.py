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
    ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL,
    POLLUTION_DISPERSAL_STARTING_DATE,
    PROVENANCE_ID,
    PROVENANCE_LINEAGE,
    PROVENANCE_NAME_POLL_ELABORATION,
    PROVENANCE_VERSION,
    SENTRY_SAMPLE_RATE,
    get_now,
)
from pollution_dispersal.manager.pollution_dispersal import PollutionDispersalManager

setup_logging("pollution-dispersal")
logger = logging.getLogger("pollution_v2.pollution_dispersal.main")

sentry_sdk.init(traces_sample_rate=SENTRY_SAMPLE_RATE)


def main() -> None:
    checkpoint_cache = None
    if COMPUTATION_CHECKPOINT_CACHE_PATH:
        logger.info(f"Checkpoint cache enabled at {COMPUTATION_CHECKPOINT_CACHE_PATH}")
        checkpoint_cache = ComputationCheckpointCache(COMPUTATION_CHECKPOINT_CACHE_PATH)

    connector_collector = ConnectorCollector.build_from_env()
    provenance = Provenance(PROVENANCE_ID, PROVENANCE_LINEAGE, PROVENANCE_NAME_POLL_ELABORATION, PROVENANCE_VERSION)
    manager = PollutionDispersalManager(connector_collector, provenance, checkpoint_cache)

    min_from_date = DEFAULT_TIMEZONE.localize(POLLUTION_DISPERSAL_STARTING_DATE) \
        if POLLUTION_DISPERSAL_STARTING_DATE.tzinfo is None else POLLUTION_DISPERSAL_STARTING_DATE
    max_to_date = DEFAULT_TIMEZONE.localize(get_now())

    # Station list comes from the domain mapping fetched inside PollutionDispersalManager.__init__
    stations = manager.get_station_list()
    station_mapping = manager.domain_mapping

    # Filter stations that appear in the domain mapping
    mapped_station_ids = {str(d["traffic_station_id"]) for d in station_mapping.values()}
    stations_to_process = []
    seen = set()
    for station in stations:
        try:
            station_id = str(station.id_stazione)
        except (ValueError, AttributeError):
            continue
        if station_id not in mapped_station_ids or station_id in seen:
            continue
        seen.add(station_id)
        meteo_code = next(
            (str(d["weather_station_id"]) for d in station_mapping.values()
             if str(d["traffic_station_id"]) == station_id),
            None,
        )
        if meteo_code:
            station.meteo_station_code = meteo_code
            stations_to_process.append(station)

    logger.info(f"Processing {len(stations_to_process)} stations")

    if not stations_to_process:
        logger.info("No stations to process")
        return

    try:
        manager.run_computation(
            stations_to_process, min_from_date, max_to_date,
            ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL, keep_looking_for_input_data=True
        )
    except Exception:
        logger.exception("Failed to run pollution dispersal computation")
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Unhandled error in pollution-dispersal job")
        sys.exit(1)
