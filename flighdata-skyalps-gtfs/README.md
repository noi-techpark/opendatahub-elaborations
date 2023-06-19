<!--
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

# flighdata-skyalps-gtfs

The following GTFS Converter is used to take data from the Sky Alps API and converting them into the GTFS format.

**Table of contents** 
- [SkyAlpsGTFS](#SkyAlpsGTFS)
 - [General information](#General-information)
	- [History](#History)
	   - [GTFS Components](#GTFS Components)
	      - [GTFS Service Classes](#GTFS Service Classes)
	         - [GTFS Service Classes Specifications](#GTFS Service Classes Specifications)

## General information: ##

General instructions can be found at the [Open Data Hub elaborations README](../README.md).

The instructions in the following paper will get you a copy of the project up and running on your local machine for development and testing purposes. 

## History: ##

SkyAlps is an Italian airline operator managing flights at the Bolzano airport in South Tyrol. Thanks to the support of NOI, SkyAlps has initiated an innovation process that aims to share the data of the air services offered. The function requested by the GTFS is to map the available data provided through the web services of the Open Data Hub (https://mobility.api.opendatahub.com/v2/flat,node/Flight) into the GTFS format specification, which foresees data to be stored in a certain number of TXT files, as summarized in the Specification file.
The agency, calendar, calendar_dates, fare_attributes, fare_rules, feed_into, frequencies, routes, shapes, stop_times, stops, transfers, and trips gtfs files are written directly from the information retrieved by the ODH API JSON. The following converter is organized into several components: 
[- Rest Template,](java/it/noitechpark/rest/FlightRest.java)
[- Dto,](java/it/noitechpark/dto)
[- Constants Classes,](java/it/noitechpark/contastsclasses)
[- Services,](java/it/noitechpark/service)
[- Enum,](java/it/noitechpark/enumClasses)

The following Converter has been designed to assist transit agency to transform existing route information from three data sources.

When you will run the converter a GTFS folder with the current timestamp attached to it will be created in the home directory of the current logged in user (See the [GTFSFolder](java/it/noitechpark/service/GTFSFolder) class (lines 15-17) for this part of the code).
In this folder you will have the .txt files filled as per request (to view the logic keep reading below or you can refer both to the [it.noitechpar.service](java/it/noitechpark/service) package classes and the [it.noitechpark package SkyApplication.java](java/it/noitechpark/SkyAlpsApplication.java) class between lines 87-258).

## GTFS Components: ##

[- Rest Template: ](java/it/noitechpark/rest/FlightRest.java)

This class is designed to make a call on the ODH API and retrieve the JSON resource template. 

[- Dto Classes: ](java/it/noitechpark/dto)

These classes represent the data that will be posted by the rest template output. This class contains also model classes for each of the specified .txt files. 
Each variable of the DTO Model Classes has been assigned the same type declared on the specification file. 

[- Constants Classes: ](java/it/noitechpark/contastsclasses)

This class defines the filenames and file fields used in the .txt files.

[- GTFS Services: ](java/it/noitechpark/service)

This section defines the GTFS output file path, and it is responsible for creating, checking, and filling each file. 

[- Enum Classes: ](java/it/noitechpark/enumClasses)
This class contains a group of constants handled by the service classes and appropriately used for each file that requires the mas for specifications. 


## GTFS Service Classes: ##

[GTFSFolder](java/it/noitechpark/service/GTFSFolder)

This class generates a GTFS folder inside the current user's Desktop folder. 
 The GTFS folder will be appended with the current Date. Appropriate checks to check if the folder already exists are performed.

[GTFSFile](java/it/noitechpark/service/GTFSFile)

This class is responsible for creating the GTFS .txt files inside the folder previously created. 

[GTFSReadFileFolder](java/it/noitechpark/service/GTFSReadFileFolder)

This class retrieves the files previously created and returns them after checking that they exist. 

[GTFSWrite](java/it/noitechpark/service/GTFSWrite)

These classes write inside the .txt files and the section defines the transit files.txt input values defined by the specifications. See below for more details. Each .txt file has been written after checks are performed on each of them.

[GTFSCheck Classes: ](java/it/noitechpark/service)

These classes check through all the conditional requirements for each of the GTFS files before they are written: 
- [GTFSCheckAgency](java/it/noitechpark/service/GTFSCheckAgency): it checks the mandatory fields.
- [GTFSCheckCalendar](java/it/noitechpark/service/GTFSCheckCalendar): it checks the mandatory fields. 
- [GTFSCheckCalendarDates](java/it/noitechpark/service/GTFSCheckCalendarDates): it checks the mandatory fields. 
- [GTFSCheckRoutes](java/it/noitechpark/service/GTFSCheckRoutes): it checks the mandatory fields and whether or not the agency_id field is mandatory or optional based on a conditional requirement that the agency.txt field contains more than a record. It also checks that either one between the short_name or long_name fields is present.
- [GTFSCheckStops](java/it/noitechpark/service/GTFSCheckStops): It checks the value of the location_type field and based on that defines whether or not the agency_id, stop_lon, and stop_lat fields might be mandatory or optional.
- [GTFSCheckStopsTimes](java/it/noitechpark/service/GTFSCheckStopsTimes): It checks the mandatory fields and whether or not the field Timepoint has a value of 1 or not. Based on the Timepoint field value it establishes if arrival_time and departure_time fields can be optional or mandatory. 
- [GTFSCheckTrips](java/it/noitechpark/service/GTFSCheckTrips): It checks the mandatory fields and whether or not inside the file Trips.txt the record has a pickup/drop-off behavior set as “continuous” and establishes if the shape_id field might be optional or mandatory. 



## GTFS Service Classes Specifications: ## 

In the first part, I will describe the .txt files and the logic of how they have been filled. For more information refer to the [specification file](documentation/230207_SpecificheIntegrazioneGTFS_NOI_v1.1 (5).pdf) where all conditions are provided.

# - FILES SPECIFICATIONS. #

1.1	Agency.txt: 

- agency_name = ID of Transit Agency, it has been left Optional.
- agency_url = Name of Transit Agency, default value: SkyAlps
- agency_timezone = URL of Transit Agency, default value: https://www.skyalps.com
- agency_id = Timezone Reference, default value: Europe/Rome
- agency_lang = Primary language reference, not supported
- agency_phone = Phone contact, not supported
- agency_fare_url = Mail contact, not supported


1.2	Stops.txt: 

- Stop_id = ID of identified Stop, Mandatory. It has been taken from the sname field of the ODH API provided. This file contains a row for each airport connected to BZO airport. Departure_airport_code and arrival_airport_code have been properly parsed. 
- Stop_code = This contains a short name, of the airport, it has been assigned the same value as the stop_id field.
- Stop_name = This contains a long name of the airport, it has been assigned the same value as the stop_id field. A check has been performed on the location_type before setting this field, for specification requirements. 
- Tts_stop_name = “Readable” version of the stop name, it is not supported and therefore it has been left empty for now. 
- Stop_desc = Contains an additional description 
- of the stop, it is not supported therefore it has been left empty for now.
- Stop_lat = This field will be provided by a second CSV file therefore it has been left empty for now. Since a conditional requirement was attached to it the same check performed to the stop_name field has been done here too.
- Stop_lon = This field will be provided by a second CSV file therefore it has been left empty for now. Since a conditional requirement was attached to it the same check performed to the stop_name field has been done here too.
- Zone_id = ID of a fare zone associated with the stop, not supported.
- Stop_url = URL of a web page dedicated to the stop, supported.
- Location_type = Refer to the enum class for this field. 
- Parent_station = Refer to the enum class for this field. The proper check is performed if location_type is present.
- Stop_timezone = Left empty, not supported.
- Wheelchair_boarding = Refer to the enum class for this field
- Level_id = Left empty, not supported.
- Platform_code = left empty, not supported. 


 
1.3	Routes.txt: 

- Route_id = This field has been filled with the departure/arrival airports code as already defined in the stop.txt file/stop_id field.
- Agency_id = Proper check has been performed on the agency.txt file
- Route_short_name = Proper check has been performed on the agency.txt file
- Route_long_name = Proper check has been performed on the agency.txt file
- Route_desc = Left empty, not supported
- Route_type = Mandatory field, check enum class
- Route_URL = Not supported, left empty
- Route_colour = Not supported, left empty but an enum class has been provided
- Route_text_colour = Not supported, left empty but an enum class has been provided
- Route_sort_order = Not supported, left empty
- Continous_pickup = Refer to Enum class for this field
- Continous_dropOff = Refer to Enum class for this field.

1.4	Trips.txt

- Route_id = same value as the routes.txt file id
- Service_id = id provided in the calendar.txt file
- Trip_id = This value has been taken from the scode field of the ODH API 
- Trip_Headisgn = same value as the stop_headsign field of the stop_times.txt file 
- Trip_short_name = Optional, left empty
- Direction_id = See the enum class
- Block_id = Optional, left empty
- Shape_id = For this field a check has been performed whether or not there is a continous_pickup or a continous_dropof f inside the stop_times.txt file
- Wheelchair_accessible = See enum class
- Bikes_allowed = See enum class
 
1.5	Stop_Times.txt

- Trip_id = It has been linked to the trips.txt and the value of it refers to the trip id
- Arrival_time = This field has been taken from the field smetadata -> sta
- Departure_time = This field has been taken from the field smetadata -> std
- Stop_id = It has been linked to the stops.txt and the value of it refers to the stop id
- Stop_Sequence
- Stop_headsign
- Pickup_type
- DropOff_type
- Continous_pickup
- Continous_dropoff
- Shape_dist_Traveled
- Timepoint
 
1.6	Calendar.txt

- Service_id = This field has been filled by taking the scode value from the ODH API provided
- Monday = See enum class true/false whether or not the flight operates on this day or not.
- Tuesday = See enum class true/false whether or not the flight operates on this day or not.
- Wednesday = See enum class true/false whether or not the flight operates on this day or not.
- Thursday = See enum class true/false whether or not the flight operates on this day or not.
- Friday = See enum class true/false whether or not the flight operates on this day or not.
- Saturday = See enum class true/false whether or not the flight operates on this day or not.
- Start_date = Starts of the service provided in a SimpleDateFormat value
- End_date = Ends of the service provided in a SimpleDateFormat value
 


1.7	Calendar_Dates.txt

- Service_id = left empty for now but links on specific fields for specifications have been made.
- Date = left empty for now but links on specific fields for specifications have been made.
- Exception_type = Left empty for now but links on specific fields for specifications have been made.
 
# - FILE CREATED: #

As requested the following .txt files are generated when running the code: 
- Agency.txt
- Stops.txt = This file contains the information of the Bolzano airport and all airports for which a flight connection exists.
- Routes.txt = This file contains the information of the connections linked to the Bolzano airport and all airports for which a flight connection exists.
- Stop_times.txt = This file contains information for each trip. Each trip has been characterized by two records in this table: one record related to the departure time at the departing airport and one record related to the arrival time at the arriving airport
- Calendar.txt = This table contains 180 records, one for each calendar day. 
- Calendar_date.txt = This table has been filled with empty values only to prove that is working.
- Fare_attributes.txt
- Fare_rules.txt
- Shapes.txt
- Frequencies.txt
- Transfers.txt
- Trips = This file contains the information on all the flights departing and arriving in Bolzano.
- Feed_info.txt
However, since only specifications for some of these files have been provided, some of them have been left empty when generated. 
