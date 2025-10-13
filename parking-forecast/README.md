<!--
SPDX-FileCopyrightText: 2021-2025 STA AG <info@sta.bz.it>
SPDX-FileContributor: Chris Mair <chris@1006.org>

SPDX-FileCopyrightText: 2025 NOI AG <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

# STA Parking Forecast
This project was initially commissioned by STA and implemented by Chris Mair, but migrated to NOI in late 2025.  

The machine learning part has stayed the same, but the data collection has been reworked in places.  

Some features like rmse calculation have been disabled.

## Overview
This projects gathers parking occupation data from the [Open Data
Hub](https://opendatahub.com/datasets) and uses that data together with weather forecast data
and information about holidays and school days. From this data,
it trains a simple, shallow neural network that can forecast occupation.

## Architecture
This application was originally running on a VM and has been dockerized when migrating from STA servers to the Open Data Hub.

The main container installs two cron jobs, one for training and one for prediction.
- training runs once every night at midnight, downloads all historical data and trains a new model. This requires around 30GB RAM and up to an hour
- prediction runs once every hour, has similar RAM requirements, but takes around 5 minutes 

A separate nginx container hosts the result, to be downloaded by the parking-forecast data collector (`/result.json`)

## Part 1/2: run-train.sh - Data Gathering and Training

The main script for this part is:

| File          | Purpose                             |
|---------------|-------------------------------------|
| run-train.sh  | gather data and start training run  |  

> Note 1: `run-train.sh` contains a hardcoded path.

> Note 2: `run-train.sh` calls among other things the `psql` executable to run SQL
> against a PostgreSQL database.  The connection information is in hardcoded in
> the script. Use `.pgpass` for the password.

### Data Gathering

The main script (`run-train.sh`) first executes SQL commands to retrieve
weather forecast data and information about holidays and school days from the
PostgreSQL database. The data is stored in CSV files **with** header. This data
is not persistent between runs - the CSV files are overwritten each time.

| File                          | Purpose                                     |
|-------------------------------|---------------------------------------------|
| data-holidays-get.sql         | query to retrieve holidays and school days  |
| (data-holidays/holidays.csv)  | resulting data                              |
| data-meteo-get.sql            | query to retrieve meteo forecasts           |
| (data-meteo/meteo.csv)        | resulting data                              |

The fields of holidays.csv are:
 - ts: ISO date
 - is_school: boolean 0/1
 - is holiday: boolean 0/1

The fields of meteo.csv are:
 - tomorrow_date: ISO date
 - symbol_value: int

The meaning of `symbol_value` is documented inside `data-meteo-get.sql`.

The other input data is the parking occupancy, also stored in CSV files, but,
updated in an incremental way:

| File       | Purpose                                                    |
|------------|------------------------------------------------------------|
| data-raw/  | parking occupancy data (one CSV file per parking station)  |

`run-train.sh` does **not** update the data of stations that
already exist in `data-raw/`, it rather just looks for new stations to be added
to the directory. This is delegated to a Node.js script:

| File                  | Purpose                                        |
|-----------------------|------------------------------------------------|
| data-raw-find-new.js  | add new stations, not yet present in data-raw/ |

The single CSV files in `data-raw/` encode the "station code" ("scode") in
their name for uniqueness and are stored **without** header. They contain the
fields:
 - timestamp: timestamp with sub second precision and time zone, such as
   "2022-01-01 00:00:00.234+0000"
 - occupancy: int

### Training

`run-train.sh` then proceeds to train five models (we use an ensemble approach)
using Python and Tensorflow.

We use the /Miniforge/ package to get Python and the required packages. A more
common Python /venv/ should do as well.  Currently, we have:

| package    | version |
|------------|---------|
| yaml       | 0.2.5   |
| pandas     | 1.3.4   |
| numpy      | 1.21.4  |
| tensorflow | 2.4.3   |

`run-train.sh` first copies the configuration file template, substituting
the timestamp of the last training data. Then it proceeds to call
**three Python scripts**. Training is typically run once a day after
midnight.  So the timestamp of the last training data is computed as yesterday,
23:55:00.

| File                                | Purpose                                                                                                                 |
|-------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| config.yaml.template                | configuration template (LAST_TRAIN_TS missing)                                                                          |
| (config.yaml)                       | configuration, temporary file during training run (overwritten and deleted after run)                                   |
| process1-raw-to-signals.py          | preprocess the data and store it into data-predictors/signals.csv and signals_interpolated.csv                          |
| process2-signals-to-trainingdata.py | read these files and create the matrix to be fed into tensorflow, store it into data-predictors/trainingdata_nonan.csv  |
| process3-fit-model.py               | perform the actual training and persist the tensorflow model to data-models/dnn_model*/                                 |

The end results of this step are the persisted tensorflow models. As we run it
five times we end up with:

| File                      |
|---------------------------|
| (data-models/dnn_model1/) |
| (data-models/dnn_model2/) |
| (data-models/dnn_model3/) |
| (data-models/dnn_model4/) |
| (data-models/dnn_model5/) |

> Note 3: These trained models are currently retrained (overwritten) once a day. However,
> they are certainly valid some time. For example, retraining could be happening
> also just once a week.

> Note 4: the model architecture is partially autoregressive, recent "holes"
> in the occupancy data cause NaN forecasts.
> It used to be that the training run downloaded **all data** starting
> from the dawn of time (2022-01-01) for each station. This was a good means
> to protect against scenario where a station doesn't send data for some time,
> but then suddenly old data becomes available. Currently, that is not possible
> due to limits imposed by the Open Data Hub. The training run only looks for
> new stations, but cannot fill holes in old data.


## Part 2/2: run-predict.sh - Do Forecasting and Publish Results

The main script of this part is:

| File           | Purpose                                                    |
|----------------|------------------------------------------------------------|
| run-predict.sh | run model inference to do forecasting and publish results  |  

> Note 5: `run-predict.sh` contains a hardcoded path.

> Note 6: `run-predict.sh` calls among other things the `psql` executable to insert
> data into a PostgreSQL database.  The connection information is in hardcoded
> in the script. Use `.pgpass` for the password.

> Note 7: `run-predict.sh` calls `sftp` to upload the forecast data to a server.
> User and hostname is hardcoded. Authentication is key based.

`run-predict.sh` first copies the configuration file
template, substituting the timestamp of the data point form which forecast
should start.

It then proceeds to **incrementally update** the parking occupancy data for
each parking station known in `data-raw/` (see above).  It never adds stations
in this step. Running forecasting would break if the number or ordering of stations
changes after training. Again, this is delegated to a Node.js script:

| File                  | Purpose                                                                                             |
|-----------------------|-----------------------------------------------------------------------------------------------------|
| data-raw-get-diff.js  | update data for stations that are already present in data-raw/ |

`run-predict.sh` then calls the first Python script again:

| File                        | Purpose                                                                                         |
|-----------------------------|-------------------------------------------------------------------------------------------------|
| process1-raw-to-signals.py  | preprocess the data and store it into data-predictors/signals.csv and signals_interpolated.csv  |

to make the new data available in the signal format.

After that, `run-predict.sh` calls, for each model:

| File                    | Purpose                                                              |
|-------------------------|----------------------------------------------------------------------|
| process4-prediction.py  | apply the model to predict the following 48 hours of occupancy data  |

The output is one CSV file for each model:

| File          |
|---------------|
| (result1.csv) |
| (result2.csv) |
| (result3.csv) |
| (result4.csv) |
| (result5.csv) |

One more step:

| File                      | Purpose                                       |
|---------------------------|-----------------------------------------------|
| process5-generate-json.py | creates a result.json file with the forecast  |

finally gives as the forecast:

| File          |
|---------------|
| (result.json) |

This is then stored in PostgreSQL and uploaded to the SFTP-Server.

The format of the `results.json` file is documented in:

| File                          |
|-------------------------------|
| readme-for-data-consumers.md  |


`run-predict.sh` is typically called once each hour.

## Other files

| File              | Purpose                                    |
|-------------------|--------------------------------------------|
| parking_utils.py  | library used by the python scripts         |
| compute-mae.py    | manually called to check forecast accuracy |
| rmse.py           | manually called to check forecast accuracy |
| graphs/           | tiny web app to plot `results.json`        |
