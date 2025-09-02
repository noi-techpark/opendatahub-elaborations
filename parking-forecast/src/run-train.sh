#!/bin/bash

PSQL="psql -h 127.0.0.1 dwh -U dwh"

# if [ "$CONDA_DEFAULT_ENV" != "tf" ]; then
#     echo "not in expected conda environment"
#     exit 1
# fi

echo ""
echo "--------------------------------------------------------------------------------"
echo "*** training run on $(date) ***"
echo "--------------------------------------------------------------------------------"


echo
echo "-> getting new stations (if there are any)"
./data-raw-find-new.js

echo
echo "-> getting holidays"
$PSQL < data-holidays-get.sql

echo
echo "-> getting meteo forecasts"
$PSQL < data-meteo-get.sql

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
