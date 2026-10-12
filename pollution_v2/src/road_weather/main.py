# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import sys
import time
from dataclasses import dataclass
from typing import Dict, List

import sentry_sdk
import yaml

from common.cache.computation_checkpoint import ComputationCheckpointCache
from common.connector.collector import ConnectorCollector
from common.data_model.common import Provenance, Station
from common.logging import setup_logging
from common.settings import (
    COMPUTATION_CHECKPOINT_CACHE_PATH,
    PROVENANCE_ID,
    PROVENANCE_LINEAGE,
    PROVENANCE_NAME_POLL_ELABORATION,
    PROVENANCE_VERSION,
    ROAD_WEATHER_CONFIG_FILE,
    SENTRY_SAMPLE_RATE,
)
from road_weather.manager.road_weather import RoadWeatherManager

setup_logging("road-weather")
logger = logging.getLogger("pollution_v2.road_weather.main")

sentry_sdk.init(traces_sample_rate=SENTRY_SAMPLE_RATE)


@dataclass
class RunSummary:
    ok: int = 0
    skipped: int = 0
    failed: int = 0
    entries: int = 0


def _fmt_duration(s: float) -> str:
    h, rem = divmod(int(s), 3600)
    m, sec = divmod(rem, 60)
    return f"{h}h{m:02}m{sec:02}s" if h else f"{m}m{sec:02}s" if m else f"{sec}s"


def load_config(path: str) -> tuple[List[str], Dict[str, str]]:
    """
    Load the road weather config: the station whitelist (all the mapped stations if empty) and the mapping between
    the ODH station code and the WRF code of the station.
    """
    with open(path, "r") as f:
        config = yaml.safe_load(f) or {}
    mappings = config.get("mappings")
    if not mappings:
        raise ValueError(f"No station mappings defined in [{path}]")
    whitelist = [str(c) for c in config.get("whitelist") or []]
    station_mapping = {str(k): str(v) for k, v in mappings.items()}
    return whitelist, station_mapping


def process_stations(manager: RoadWeatherManager, stations: List[Station],
                     station_mapping: Dict[str, str]) -> RunSummary:
    """
    Compute the road condition forecast for each station. A failure on a station does not stop the others.
    """
    summary = RunSummary()
    for station in stations:
        if str(station.code) not in station_mapping:
            logger.error(f"Station {station.code} not found in road weather config mapping, skipping")
            summary.skipped += 1
            continue
        station.wrf_code = station_mapping[str(station.code)]
        logger.info(f"Processing station {station.code} (WRF code: {station.wrf_code})")
        try:
            n = manager.run_computation_for_single_station(station)
            summary.entries += n
            if n == 0:
                summary.skipped += 1
            else:
                summary.ok += 1
        except Exception:
            logger.exception(f"Failed to process station {station.code}")
            summary.failed += 1
    return summary


def main() -> None:
    whitelist, station_mapping = load_config(ROAD_WEATHER_CONFIG_FILE)

    checkpoint_cache = None
    if COMPUTATION_CHECKPOINT_CACHE_PATH:
        logger.info(f"Checkpoint cache enabled at {COMPUTATION_CHECKPOINT_CACHE_PATH}")
        checkpoint_cache = ComputationCheckpointCache(COMPUTATION_CHECKPOINT_CACHE_PATH)

    connector_collector = ConnectorCollector.build_from_env()
    provenance = Provenance(PROVENANCE_ID, PROVENANCE_LINEAGE, PROVENANCE_NAME_POLL_ELABORATION, PROVENANCE_VERSION)
    manager = RoadWeatherManager(connector_collector, provenance, checkpoint_cache)

    stations = manager.get_station_list()
    if whitelist:
        stations = [s for s in stations if str(s.code) in whitelist]
    logger.info(f"Processing {len(stations)} stations")

    t_job = time.monotonic()
    summary = process_stations(manager, stations, station_mapping)

    logger.info(
        f"Run summary: stations={summary.ok}ok/{summary.skipped}skipped/{summary.failed}failed  "
        f"entries={summary.entries}  elapsed={_fmt_duration(time.monotonic() - t_job)}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Unhandled error in road-weather job")
        sys.exit(1)
