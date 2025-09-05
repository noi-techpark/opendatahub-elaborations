#!/bin/bash

# SPDX-FileCopyrightText: 2025 NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: CC0-1.0

source /conda/etc/profile.d/conda.sh
conda activate tf

if [ "$RUN_IMMEDIATELY" == "true" ]; then 
    echo "Running jobs immediately:"
    ./run-train.sh
    ./run-predict.sh
fi

# setup cron jobs
echo "$CRON_TRAIN /code/run-train.sh > /dev/stdout 2>&1" > /etc/cron.d/train
echo "$CRON_PREDICT /code/run-predict.sh > /dev/stdout 2>&1" > /etc/cron.d/predict

# wait forever to keep container alive
sleep infinity