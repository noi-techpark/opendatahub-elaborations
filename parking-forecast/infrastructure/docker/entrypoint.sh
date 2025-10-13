#!/bin/bash

# SPDX-FileCopyrightText: 2025 NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: CC0-1.0


# propagate env variables to cron jobs
env | sed -e '/^CRON_/d' > /etc/environment

echo 'source /conda/etc/profile.d/conda.sh' >> /etc/environment
echo 'conda activate tf' >> /etc/environment

# mainly for debugging and testing
if [ "$RUN_IMMEDIATELY" == "true" ]; then 
    echo "Running jobs immediately:"
    source /etc/environment
    ./run-train.sh
    echo "Training done. Running prediction"
    ./run-predict.sh
    echo "Prediction done"
fi

# redirect cron job output to PID 1 stdout (the file monitored by docker)
stdout=/proc/1/fd/1
# setup cron jobs
crontab - <<EOF
SHELL=/bin/bash
$CRON_TRAIN (cd /code; source /etc/environment; ./run-train.sh) > $stdout 2>&1
$CRON_PREDICT (cd /code; source /etc/environment; ./run-predict.sh) > $stdout 2>&1
EOF

echo "Starting cron with schedule:"
crontab -l
echo
cron -f -L 4
