#!/bin/bash

# SPDX-FileCopyrightText: 2025 NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: CC0-1.0

source /conda/etc/profile.d/conda.sh
conda activate tf

# propagate env variables to cron jobs
env > /etc/environment

# mainly for debugging and testing
if [ "$RUN_IMMEDIATELY" == "true" ]; then 
    echo "Running jobs immediately:"
    ./run-train.sh
    ./run-predict.sh
fi

# redirect cron job output to PID 1 stdout (the file monitored by docker)
stdout=/proc/1/fd/1
# setup cron jobs
crontab - <<EOF
$CRON_TRAIN /code/run-train.sh > $stdout 2>&1
$CRON_PREDICT /code/run-predict.sh > $stdout 2>&1
EOF

echo "Starting cron with schedule:"
crontab -l
echo
cron -f -L 4
