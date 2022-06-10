#!/usr/bin/env python3

import os

env_keys = list(dict(os.environ).keys())

prefix = "LAMBDA_"
output = []


print("{", end="")
for key in env_keys:
    if key.startswith(prefix):
        print(f"{key.split(prefix, 1)[1]}={os.environ.get(key)}", end="")
print("}", end="")

# if output:
#     print(f'{{{",".join(output)}}}')
