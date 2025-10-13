<!--
SPDX-FileCopyrightText: 2021-2025 STA AG <info@sta.bz.it>
SPDX-FileContributor: Chris Mair <chris@1006.org>

SPDX-License-Identifier: CC0-1.0
-->

# Parking Forecast

(C) 2022 [STA](https://www.sta.bz.it/)

## Information for data consumers

NOI Techpark's [Open Data Hub](https://opendatahub.com/) gathers occupancy data
from regional car parks.
The occupancy time series can be queried using an open API
( [an open API](https://opendatahub.com/datasets/traffic/parking/) ) or
[an interactive tool](https://analytics.opendatahub.com/).

STA takes this data and computes a forecast once an hour.
New forecast are available ~ 12 minutes past the hour each hour from 3:00
to 23:00 UTC. The forecasts start 5 minutes past the hour with a 5-minute
resolution and span 48 hours.

The latest forecast is available in JSON format from:

https://web01.sta.bz.it/parking-forecast/result.json

Top-level keys are:

```
publish_timestamp            timestamp when this forecast was published (string),
                             e.g. "2022-01-20 10:11:49.108211+00:00"

forecast_start_timestamp     timestamp of first predicted data point  (string),
                             e.g. "2022-01-20 10:05:00+00:00"
                             
forecast_period_seconds      timeseries resolution in seconds (number), currently always 300

forecast_duration_hours      timeseries total length in hours (number), currently always 48

model_version                version of forcasting model (string), currently "1.1"

schema_version               version of this JSON schema (string), currently "1.1"

timeseries                   data points
```

`timeseries` is an object with the car park station codes (*scode*) as keys.
The list and metadata of these station codes can be queried from the Open Data Hub via:

http://mobility.api.opendatahub.com/v2/flat/ParkingStation%2CParkingSensor

In particular, metadata contains name, municipality, geographic coordinates and maximum
occupancy for each car park.

The value of each *scode* is an array of data points with keys:

```
ts     timestamp (string), e.g. "2022-01-20 10:05:00+00:00"

lo     lower estimate for occupancy (number or null), e.g. 260.4

mean   arithmetic average between lo and hi (number or null), e.g. 262

hi     upper estimate for occupancy (number or null), e.g. 264.4

rmse   RMSE computed from past (30 - 2 days ago) forecasts
       compared to actual data (number or null), e.g. 10.2
```

Note the values can be null. This happens when a parking station
has not sent up to date data.

Note that the error as given by `hi` - `lo` is just a measure
of numerical stability of the model, not a confidence bound. 
The RMSE can be used as a estimate of confidence.

## Legal Information

The parking forecasts as distributed on

https://web01.sta.bz.it/parking-forecast/result.json

are Open Data. They are released under the same licence as the occupancy
data from the Open Data Hub, from which they are computed
(see [the Open Data Hub license page](https://docs.opendatahub.com/en/latest/licenses.html#odh-license)).

The parking forecasts are to be considered experimental. There is absolutely
no warranty on availability or quality of the data.


## Changelog of this document

- 2022-11-08 - from now on predictions are computed 21 times a day (3-23 hours) instead of 22 times a day
- 2022-04-26 - added info about new timeseries field "rmse" and schema version bumped to 1.1
- 2022-01-20 - document created 
