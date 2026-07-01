#!/bin/bash

# SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests
from datetime import date, timedelta
import csv
import sys

def fetch_events(tag):
    url = f"https://tourism.api.opendatahub.com/v1/Event?rawfilter=and(like(Tags,'{tag}'))&pagesize=100"
    response = requests.get(url)
    return response.json()['Items']


def expand_dates(school_holidays, public_holidays):
    # the event returned from the API has DateBegin and a DateEnd.
    # expanding theranges into individual dates and then check each day independently if it is a school holiday 
    # or public holiday

    school_holiday_dates = set()
    public_holiday_dates = set()

    for event in school_holidays:
        date_begin = date.fromisoformat(event['DateBegin'][:10])
        date_end = date.fromisoformat(event['DateEnd'][:10])
        current = date_begin
        while current <= date_end:
            school_holiday_dates.add(current)
            current += timedelta(days=1)

    for event in public_holidays:
        date_begin = date.fromisoformat(event['DateBegin'][:10])
        date_end = date.fromisoformat(event['DateEnd'][:10])
        current = date_begin
        while current <= date_end:
            public_holiday_dates.add(current)
            current += timedelta(days=1)

    return school_holiday_dates, public_holiday_dates


school_holidays = fetch_events('school holiday')
public_holidays = fetch_events('public holiday')
print(f"Fetched {len(school_holidays)} school holiday events")
print(f"Fetched {len(public_holidays)} public holiday events")

school_holiday_dates, public_holiday_dates = expand_dates(school_holidays, public_holidays)

# combine the school holiday and public holiday dates to find the earliest and latest dates as a starting point for the CSV file
all_dates = school_holiday_dates | public_holiday_dates
all_dates_start = min(all_dates)
all_dates_end = max(all_dates)

csv_file = 'data-holidays/holidays.csv'

with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ts', 'is_school', 'is_holiday'])
    current = all_dates_start
    while current <= all_dates_end:
        is_weekend = current.weekday() >= 5  # 5=Saturday, 6=Sunday
        is_school_holiday = current in school_holiday_dates
        is_public_holiday = current in public_holiday_dates
        is_school = 0 if (is_weekend or is_school_holiday or is_public_holiday) else 1
        is_holiday = 1 if (is_public_holiday or is_weekend) else 0
        writer.writerow([current, is_school, is_holiday])
        current += timedelta(days=1)

print(f"Written rows from {all_dates_start} to {all_dates_end} to {csv_file}")