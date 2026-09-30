# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from dataprocessor.DataProcessor import Processor
import logging
import os
import time

log = logging.getLogger()

def main():
    processor = Processor()
    schedule_sec = int(os.environ.get("JOB_SCHEDULE_SEC", "10"))
    # Runs as a long-lived loop (instead of one process per run) so
    # Processor's in-memory state (e.g. the uncalibratable-station cache)
    # survives across elaboration runs.
    while True:
        log.info('Elaboration start')
        try:
            processor.calc_by_station()
        except Exception:
            log.exception('Elaboration run failed')
        log.info('Elaboration end')
        time.sleep(schedule_sec)

if __name__ == "__main__":
    main()
