<!--
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

# flighdata-skyalps-gtfs

This GTFS Converter is used to take data from the Sky Alps API and convert them into the GTFS format.

## General information: ##

General instructions can be found at the [Open Data Hub elaborations README](../README.md).

## History: ##

SkyAlps is an Italian airline operator managing flights at the Bolzano airport in South Tyrol. Thanks to the support of NOI, SkyAlps has initiated an innovation process that aims to share the data of the air services offered. The function requested by the GTFS is to map the available data provided through the web services of the Open Data Hub (https://mobility.api.opendatahub.com/v2/flat,node/Flight) into the GTFS format specification, which foresees data to be stored in a certain number of TXT files, as summarized in the Specification file.
The agency, calendar, calendar_dates, fare_attributes, fare_rules, feed_into, frequencies, routes, shapes, stop_times, stops, transfers, and trips gtfs files are written directly from the information retrieved by the ODH API JSON.

When you will run the converter a GTFS folder with the current timestamp attached to it will be created in the home directory of the current logged in user.
