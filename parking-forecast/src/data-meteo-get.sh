#!/bin/bash

datefrom=2021-12-31
csv=data-meteo/meteo.csv

if [ -f $csv ]; then
    line_count=$(wc -l < "$csv")
    if [ "$line_count" -gt 1 ]; then
        datefrom=`tail -n 1 "$csv" | cut -d',' -f1 | tr -d '"'`
        echo "Existing weather file was found. Starting request from latest date $datefrom"
    fi
fi

curl "https://tourism.api.opendatahub.com/v1/WeatherHistory?rawsort=_Meta.LastUpdate&fields=Weather.en.Stationdata&pagesize=0&datefrom=$datefrom" \
| jq -r '.Items[].["Weather.en.Stationdata"][] | select(.Id == 3) | [.date, .Weathercode] | @csv' \
| sed 's/T[0-9:]*//g' > $csv.tmp

if [ -s $csv.tmp ]; then
    echo "New weather data found. Adding to csv"
    {
        echo "tomorrow_date,symbol_value";
        {
            cat $csv | tail -n +2; \
            cat $csv.tmp 
        } | awk -F',' '{codes[$1] = $2} END {for (date in codes) print date "," codes[date]}' | sort
    } > $csv
else
    echo "No new weather data has been found :("
fi

rm $csv.tmp

echo "Job done"