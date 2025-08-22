#!/bin/bash

set -e

cd /data/ml/sit-sta-modules/parking-production || exit 1

if [ "$CONDA_DEFAULT_ENV" != "tf" ]; then
    echo "not in expected conda environment"
    exit 1
fi

echo ""
echo "--------------------------------------------------------------------------------"
echo "*** prediction run on $(date) ***"
echo "--------------------------------------------------------------------------------"

echo "-> updating raw parking data from the ODH"
./data-raw-get-diff.js

echo
echo "-> creating config.yaml.tmp from template"
LAST_FULL_HOUR=$(date +'%F %H')
cp config.yaml.template config.yaml.tmp
sed -i "s/__LAST_TRAIN_TS__/${LAST_FULL_HOUR}:00:00+00:00/" config.yaml.tmp
cat config.yaml.tmp

echo
echo "-> process1: (re)building predictors"
cp config.yaml.tmp config.yaml
python3 process1-raw-to-signals.py
rm -f config.yaml

echo
for MODEL_NUM in 1 2 3 4 5; do
    OUTPUT_FILENAME="result${MODEL_NUM}.csv"
    echo "-> process4: run prediction to ${OUTPUT_FILENAME}"
    cp config.yaml.tmp config.yaml
    sed -i "s/__OUTPUT__/${OUTPUT_FILENAME}/" config.yaml
    python3 process4-prediction.py ${MODEL_NUM}          # RES max 7 GB
    rm -f config.yaml
done

echo
echo "-> process5: generate JSON"
cp config.yaml.tmp config.yaml
python3 process5-generate-json.py
rm config.yaml

rm -f config.yaml.tmp

echo
echo "-> upload JSON"
echo "put result.json /var/www/html/parking-forecast/result.json" | /bin/sftp -b - parking-forecast@web01.sta.bz.it

echo
echo "-> save JSON"
psql -U dwh -c "\copy parking_forecast.history(data) from 'result.json'"



