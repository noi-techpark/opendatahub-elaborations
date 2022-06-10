#!/usr/bin/env python3

import os

env_keys = list(dict(os.environ).keys())

prefix = "LAMBDA_"
output = []


for key in env_keys:
    if key.startswith(prefix):
        output.append(f"{key.split(prefix, 1)[1]}={os.environ.get(key)}")

print(f'{{{",".join(output)}}}')
