# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import sys
import time

import sentry_sdk
import yaml

from common.connector.collector import ConnectorCollector
from common.data_model.common import Provenance
from common.logging import setup_logging
from common.settings import (
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


def _fmt_duration(s: float) -> str:
    h, rem = divmod(int(s), 3600)
    m, sec = divmod(rem, 60)
    return f"{h}h{m:02}m{sec:02}s" if h else f"{m}m{sec:02}s" if m else f"{sec}s"


def main() -> None:
    with open(ROAD_WEATHER_CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
    whitelist = [str(c) for c in config.get("whitelist", [])]
    station_mapping = {str(k): str(v) for k, v in config["mappings"].items()}

    connector_collector = ConnectorCollector.build_from_env()
    provenance = Provenance(PROVENANCE_ID, PROVENANCE_LINEAGE, PROVENANCE_NAME_POLL_ELABORATION, PROVENANCE_VERSION)
    manager = RoadWeatherManager(connector_collector, provenance)

    stations = manager.get_station_list()
    if whitelist:
        stations = [s for s in stations if str(s.code) in whitelist]
    logger.info(f"Processing {len(stations)} stations")

    t_job = time.monotonic()
    total_entries = 0
    ok = skipped = failed = 0
    for station in stations:
        if str(station.code) not in station_mapping:
            logger.error(f"Station {station.code} not found in road weather config mapping — skipping")
            skipped += 1
            continue
        station.wrf_code = station_mapping[str(station.code)]
        logger.info(f"Processing station {station.code} (WRF code: {station.wrf_code})")
        try:
            n = manager.run_computation_for_single_station(station)
            total_entries += n
            if n == 0:
                skipped += 1
            else:
                ok += 1
        except Exception:
            logger.exception(f"Failed to process station {station.code}")
            failed += 1

    logger.info(
        f"Run summary: stations={ok}ok/{skipped}skipped/{failed}failed  "
        f"entries={total_entries}  elapsed={_fmt_duration(time.monotonic() - t_job)}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Unhandled error in road-weather job")
        sys.exit(1)
