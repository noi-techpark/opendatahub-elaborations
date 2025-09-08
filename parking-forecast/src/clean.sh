#!/bin/bash

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