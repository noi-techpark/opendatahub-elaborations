#!/bin/bash

# SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

csv=data-holidays/holidays.csv

# If we already have data, extract the last date and pass it to the Python script
# so it only fetches new data from that point on
if [ -f $csv ]; then
    line_count=$(wc -l < "$csv")
    if [ "$line_count" -gt 1 ]; then
        datefrom=`tail -n 1 "$csv" | cut -d',' -f1`
        echo "Existing holidays file was found. Starting request from latest date $datefrom"
    fi
fi

# Call the Python script to fetch and generate the holidays CSV
python3 data-holidays-get.py

echo "Job done"