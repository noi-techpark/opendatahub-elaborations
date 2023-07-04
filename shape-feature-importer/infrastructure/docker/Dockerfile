# image could be replaced with official postgis docker image but currently it gives an error
FROM debian:buster-slim

RUN apt-get update \
      && apt-get install -y --no-install-recommends \
           postgis \
           postgresql-client-11

