
# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: CC0-1.0
FROM debian:trixie-slim AS env
RUN apt update
RUN apt install -y wget curl nodejs jq cron
RUN apt clean

# install miniforge (conda alternative) https://github.com/conda-forge/miniforge
RUN wget -O /Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
RUN bash /Miniforge3.sh -b -p /conda
RUN rm /Miniforge3.sh

# Setup python environment
COPY src/requirements.txt .
RUN <<EOF bash
    source /conda/etc/profile.d/conda.sh
    conda activate
    conda create --name tf -y --file requirements.txt
EOF

COPY infrastructure/docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]

RUN mkdir /code
WORKDIR /code

FROM env AS build
COPY src/ .