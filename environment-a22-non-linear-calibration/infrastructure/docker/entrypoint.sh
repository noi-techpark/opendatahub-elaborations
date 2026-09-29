#/bin/bash
# exit if error
set -e
# main.py now loops internally every JOB_SCHEDULE_SEC so its in-memory
# state (e.g. the uncalibratable-station cache) survives across runs.
python /usr/src/app/main.py > /proc/1/fd/1 2>/proc/1/fd/2
