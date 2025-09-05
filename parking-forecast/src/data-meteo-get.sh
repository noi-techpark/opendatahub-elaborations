#!/bin/bash

datefrom=2021-12-31
csv=data-meteo/meteo.csv

# If we already have data, extract the last entry end request new weather only from that point on
if [ -f $csv ]; then
    line_count=$(wc -l < "$csv")
    if [ "$line_count" -gt 1 ]; then
        datefrom=`tail -n 1 "$csv" | cut -d',' -f1 | tr -d '"'`
        echo "Existing weather file was found. Starting request from latest date $datefrom"
    fi
fi

# Get the weather Json, then:
# 1) extract the Stationdata structure with ID=3, and then create a csv using only the "date" and "WeatherCode" fields.
#    Note that this often gives duplicate entries for a given date, since we have the ID=3 for today and tomorrow in the same structure.
#    Unfortunately we cannot rely on the API always giving us values for both days, so we make due with either one.
#    We will clean up these duplicates afterwards
# 2) strip the timestamp component of the date
# 3) convert the a-z weather code to it's ascii representation, and then subtract 97 to have it 0-based, since that's what the model expects
curl -s "https://tourism.api.opendatahub.com/v1/WeatherHistory?rawsort=_Meta.LastUpdate&fields=Weather.en.Stationdata&pagesize=0&datefrom=$datefrom" \
| jq -r '.Items[].["Weather.en.Stationdata"][] | select(.Id == 3) | [.date, .WeatherCode] | @csv' \
| sed 's/T[0-9:]*//g' \
| awk -F',' 'BEGIN{OFS=","; for(i=0;i<256;i++) ord_map[sprintf("%c",i)]=i-97} {gsub(/"/, "", $2); $2 = sprintf("\"%d\"", ord_map[substr($2,1,1)]); print}' \
> $csv.tmp

if [ -s $csv.tmp ]; then
    # Note: The braces are there to concatenate the output of all comands inside to a single stream.
    # All the output from within these braces will be part of the csv file
    echo "New weather data found. Adding to csv"
    {
        # write the csv header
        echo "tomorrow_date,symbol_value";
        {
            # cat the old csv, leaving out the header (we created a new one above)
            # splice it together with the newly downloaded data
            cat $csv | tail -n +2; \
            cat $csv.tmp 
            # Now we need to clean up possible duplicates for the same date. 
            # We take the last one we find, as that's probably a "today" prediction and more accurate than a "tomorrow" one
        } | sort | awk -F',' '{codes[$1] = $2} END {for (date in codes) print date "," codes[date]}' | sort
    } > $csv
else
    echo "No new weather data has been found :("
fi

rm $csv.tmp

echo "Job done"