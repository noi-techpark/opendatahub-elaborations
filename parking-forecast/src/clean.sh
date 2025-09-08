#!/bin/bash

# SPDX-FileCopyrightText: 2025 NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# cleanup remnants of incomplete job. 
# mostly for local development, the job shouldn't care either way

# must run with sudo if using with docker container

rm -rf __pycache__
rm -rf data-models/*
rm data-predictors/*.csv
rm data-raw/*.csv
rm data-raw-candidate/*.csv
rm config.yaml
rm result.json
rm result*.csv