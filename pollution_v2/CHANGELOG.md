<!--
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

# Changelog

[[_TOC_]]

## Version 2025.*

### (next release)

:bug: Bug fixes
* On stations not sending data, checkpoint is not anymore incremented by 1 day each DAG execution.
* The pollution computer consider as ending date today at the previous midnight, to comply with validator processing from midnight to midnight.

:nail_care: Polish
* All datetimes in logs are expressed using ISO format.

### 2025.01.31

:rocket: New features
* Added creation of `EnvironmentStation` for computed pollution dispersal entries.
* Added retrieval of weather measures from road weather stations for pollution dispersal computation.
* Added deletion of temporary files after computation.

## Version 2024.*

### 2024.12.20

:rocket: New features
* Added pollution dispersal computation.

### 2024.10.29

:rocket: New features
* Road condition saved as string (instead of int value).
* Added road condition forecast confidence interval.

### 2024.10.14

:rocket: New features
* RoadWeather DAG running as a DAG:
  * Road weather data read from ODH,
  * Road weather forecasts coming from WS on dedicated METRo container,
  * METRo XML output parsed and written on ODH.

### 2024.02.23

:rocket: New features
* Airflow as workflow management.
* Draft for data validation workflow.
* Deployment on https://noi.u-hopper.com.
