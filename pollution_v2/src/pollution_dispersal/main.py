# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import sys
import time
from datetime import timedelta

import sentry_sdk

from common.cache.computation_checkpoint import ComputationCheckpointCache
from common.connector.collector import ConnectorCollector
from common.data_model.common import Provenance
from common.logging import setup_logging
from common.manager.traffic_station import RunStats
from common.settings import (
    COMPUTATION_CHECKPOINT_CACHE_PATH,
    DEFAULT_TIMEZONE,
    ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL,
    POLLUTION_DISPERSAL_COMPUTATION_HOURS_SPAN,
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


def _fmt_duration(s: float) -> str:
    h, rem = divmod(int(s), 3600)
    m, sec = divmod(rem, 60)
    return f"{h}h{m:02}m{sec:02}s" if h else f"{m}m{sec:02}s" if m else f"{sec}s"


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

    t_job = time.monotonic()
    total = RunStats()
    iteration = 0
    while True:
        iteration += 1
        max_to_date = DEFAULT_TIMEZONE.localize(get_now())
        logger.info(f"Catch-up iteration {iteration}: processing up to {max_to_date.isoformat()}")

        try:
            total += manager.run_computation(
                stations_to_process, min_from_date, max_to_date,
                ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL, keep_looking_for_input_data=True
            )
        except Exception:
            logger.exception("Failed to run pollution dispersal computation")
            raise

        new_start, _ = manager.get_starting_date(
            manager.get_output_connector(), manager.get_input_connector(),
            stations_to_process, min_from_date, ODH_COMPUTATION_BATCH_SIZE_POLL_DISPERSAL,
            keep_looking_for_input_data=False,
        )
        new_now = DEFAULT_TIMEZONE.localize(get_now())
        caught_up = (
            new_start is None
            or new_start >= (new_now - timedelta(hours=POLLUTION_DISPERSAL_COMPUTATION_HOURS_SPAN))
        )
        if caught_up:
            logger.info(f"Caught up to current time after {iteration} iteration(s)")
            break
        logger.info(
            f"Still {(new_now - new_start).total_seconds() / 3600:.1f} hour(s) behind "
            f"after iteration {iteration}, running again"
        )

    date_range = (f"{total.date_from.date()} -> {total.date_to.date()}"
                  if total.date_from and total.date_to else "no data")
    logger.info(
        f"Run summary: stations={len(stations_to_process)}  iterations={iteration}  "
        f"batches={total.batches}  entries={total.entries}  "
        f"elapsed={_fmt_duration(time.monotonic() - t_job)}  range={date_range}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Unhandled error in pollution-dispersal job")
        sys.exit(1)
