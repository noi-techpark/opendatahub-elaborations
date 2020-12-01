#!/bin/bash
pip install --no-cache-dir -r requirements.txt -t ./src
cd src && zip -r /data/freeParkingSlotsCalculator.zip .
python -c 'import lambdaInit;lambdaInit.handleLambdaCall(1,2)'
