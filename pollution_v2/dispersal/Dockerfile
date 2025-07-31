# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt-get install -y gfortran
RUN apt-get install -y make
RUN apt-get install -y gdal-bin
RUN apt-get install -y libgdal-dev
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y sed
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app/

# install Python requirements
RUN pip3 install -r requirements.txt

WORKDIR /app/RLINE
RUN make -f Makefile.gfortran
RUN ls -R

WORKDIR /app/src

ENV PYTHONPATH="."
ENV LOG_TO_FILE=1
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

CMD ["fastapi", "run", "webserver/ws.py", "--port", "80"]
