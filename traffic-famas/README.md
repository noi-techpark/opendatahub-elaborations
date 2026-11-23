<!--
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

# Traffic FAMAS hourly elaboration

Aggregates the 5 minute traffic data of the FAMAS stations (province of Bolzano, origin `FAMAS-traffic-provinceBZ`, station type `TrafficSensor`)
to hourly values. The raw data is written by the [traffic-famas-prov-bz transformer](https://github.com/noi-techpark/odh-mobility-transformers).

```
traffic-famas-prov-bz   (period 300s)  -->  traffic-famas   (period 3600s)
```

## Data types and aggregation

All 16 data types of the transformer are elaborated to hourly values:

| Data types | Aggregation |
|---|---|
| `total-transits`, `number-of-*` (vehicle classes) | sum |
| `average-vehicle-speed`, `headway`, `headway-variance`, `gap`, `gap-variance` | average |

The aggregation is configured per type in `dataTypes` in `src/main.go` (`sum` or `avg`; more can be added in `aggregations` in `src/aggregate.go`).
If you change it on a running deployment, already written hourly records keep their old meaning (same type name and period), so reset them first.

The elaborated records **keep the data type name** and only differ by period (3600). This is the same convention as
`environment-a22-averages` and `traffic-a22-data-quality`. The data types themselves are owned by the collector and are not synced by this elaboration.

## Windows

* Windows are aligned to the full hour (UTC), half-open `[start, end)`, and the result is timestamped with the window **end**.
* A window is only written once it is complete (the last 5 minute bucket arrived) and has at least `MIN_SAMPLES` (default 6 of 12) records for that data type.
* The elaboration library takes care of catching up from the last written hourly record.

## Configuration

See [.env.example](.env.example). Run locally with `docker compose up` after creating a `.env` (client secret needed, this is not open data).
Tests: `cd src && go test ./...`
