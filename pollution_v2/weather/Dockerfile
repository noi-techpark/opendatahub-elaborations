# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt upgrade -y
RUN apt install -y --no-install-recommends python3.10 python3.10-dev python3-pip
RUN python3.10 -m pip install --upgrade pip
RUN apt install -y --no-install-recommends build-essential python3-libxml2 swig gfortran cpio curl

WORKDIR /app

COPY . /app/

# install Python requirements
RUN pip install -r requirements.txt

# setup METRo
# see https://framagit.org/metroprojects/metro/-/wikis/Installation_(METRo)
ENV PYTHON_INCLUDE="/usr/include/python3.10"
RUN /app/metro/setup.sh /usr/local/

WORKDIR /app/src

ENV PYTHONPATH="."
ENV MAIN_DIR="/app"
ENV LOG_TO_FILE=1

CMD ["fastapi", "run", "webserver/ws.py", "--port", "80"]
