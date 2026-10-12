<!--
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

# METRo

The road condition forecasts of the `road-weather` job are computed by the METRo model
([wiki](https://framagit.org/metroprojects/metro/-/wikis/METRo)), whose sources are in `metro`.

The job runs it as a subprocess: the job `Dockerfile` (`infrastructure/docker/Dockerfile`) builds it, and it
runs on the Debian system python, since it needs the python-libxml2 bindings. The only change to the original sources
is replacing `numpy.float`, removed from recent numpy versions, with `float` at build time.

The station parameters METRo needs (`parameters_<WRF code>.xml`) are in `src/config/metro`. `_test_only` has sample
inputs and outputs of METRo.
