ts-model README
================
Copyright (c) 2013 by Martin Reinstadler 
Published under the Library GNU Public License (LGPL)


1. Introduction
2. Directory Overview
3. Prerequisites
4. Usage
5. Credits


1. Introduction
---------------
This is a cron-job, designed to run each hour on a web-server and. It
generates predictions for parking lots and saves them in an XML file, 
that can be read by an appropriate web-service

ts-model is a straightforward, simple-to-use 100% pure Java solution. 


2. Directory Overview
---------------------

/README.txt ......... This file
/LICENSE.txt ........ ts-model license
/TODO.txt ........... Known issues and bugs
/RELEASE.txt ........ Release change notes
/doc/ ............... HTML documentation (usage, configuration etc.)
/TS-Model.jar ......,.the standalone application
/pom.xml .............maven pom file
/src .................source code
/target ..............empty folder (maven deploy target)
/tsmodel.log .........log file 
/external.properties .application configuration needed also by the web service 
 

3. Prerequisites
----------------
ParkinPrediction requires Tomcat server and Java running on it

4. Usage
--------
ts-model runs alone as cron job each hour. In order to use it on your own server
you must configure the project settings in the following way:
1) src/main/resources/META-INF/spring/applicationContext.xml - set the path to the properties file
2) src/main/resources/META-INF/spring/database.properties - set the connection properties
to your postgres.sql file
3) configure the external_properties file for your needs and place it on the location
defined in the applicationContext.xml
4) Configure your html-connection (if outside the university of Bolzano) in the two 
java classes it.unibz.tsmodel.parser.tis.TisDataReader and
it.unibz.tsmodel.overlay.weather.OWMReader
5) deploy the project again and put the jar file on your server

5. Credits
----------

Website Location:

  https://bitbucket.org/sipai/sipai-mobile/wiki/Time%20Series%20Analysis

ts-model written by:

  Martin Reinstadler


Additional code, fixes and improvements by:

  Matthias Braunhofer


  and many other users and testers.
  
  
(If your name is missing here - sorry. 
 Just remind me to add it!)

WEKA library written by:

  Mark Hall & collaborators of the 
  University of Waikato: Department of Computer Science



