#!/bin/bash

# SPDX-FileCopyrightText: 2021-2025 STA AG <info@sta.bz.it>
# SPDX-FileContributor: Chris Mair <chris@1006.org>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

if [ "$CONDA_DEFAULT_ENV" != "tf" ]; then
    echo "not in expected conda environment"
    exit 1
fi

echo ""
echo "--------------------------------------------------------------------------------"
echo "*** training run on $(date) ***"
echo "--------------------------------------------------------------------------------"

echo "-> getting new auth token"
export oauth_token=$(./get-oauth-token.sh 2>&1) || {
    echo "Error: Failed to obtain OAuth token - $oauth_token" >&2
    exit 1
}

echo
echo "-> getting raw data"

# load all the car park data into data-raw-candidate/;
# if the download succeeds, remove the old data files from data-raw
# and move the new ones from data-raw-candidate to data-raw,
# otherwise remove data-raw-candidate and keep everything as is

mkdir -p data-raw-candidate
./data-raw-get.js

if [ $? -eq 0 ]; then
    echo "  -> success"
    rm    -f data-raw/*csv
    mv    data-raw-candidate/*csv data-raw/
else
    echo "  -> failure"
    rm    -f data-raw-candidate/*csv
fi


echo
echo "-> getting holidays"
# not implemented

echo
echo "-> getting meteo forecasts"
./data-meteo-get.sh

echo
echo "-> creating config.yaml from template"
YESTERDAY=$(date --iso -d '1 day ago')
cp config.yaml.template config.yaml
sed -i "s/__LAST_TRAIN_TS__/${YESTERDAY} 23:55:00+00:00/" config.yaml
cat config.yaml

echo
echo "-> process1: building predictors"
python3 process1-raw-to-signals.py

echo
echo "-> process2: building training data"      
python3 process2-signals-to-trainingdata.py             # RES max 11 GB

echo
for MODEL_NUM in 1 2 3 4 5; do
    echo "-> process3: train model ${MODEL_NUM}"       
    python3 process3-fit-model.py ${MODEL_NUM}          # RES max 19 GB
done 
rm -f config.yaml
