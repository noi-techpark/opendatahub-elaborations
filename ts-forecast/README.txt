ts-forecast README
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
ts-forecst is a web service that reads parking lot predictions and answers
with JSON to web-requests

ts-forecast is a straightforward, simple-to-use 100% pure Java solution. 


2. Directory Overview
---------------------

/README.txt ......... This file
/LICENSE.txt ........ ts-forecast license
/TODO.txt ........... Known issues and bugs
/RELEASE.txt ........ Release change notes
/doc/ ............... HTML documentation (usage, configuration etc.)
/ts-forecast.jar ......,.the standalone application
/pom.xml .............maven pom file
/src .................source code
/target ..............maven deploy target
/external.properties .application configuration needed also by the web service 
 

3. Prerequisites
----------------
ts-forecast requires Tomcat server and Java running on it

4. Usage
--------
ts-forecast waits for web-requests and answers with JSON. In order to place it on 
your own server:
1) src/main/resources/META-INF/spring/applicationContext.xml - set the path to the properties file
2) configure the external_properties file for your needs and place it on the location
defined in the applicationContext.xml

5. Credits
----------

Website Location:

  https://bitbucket.org/sipai/sipai-mobile/wiki/Time%20Series%20Analysis

ts-forecast written by:

  Martin Reinstadler


Additional code, fixes and improvements by:

  Matthias Braunhofer


  and many other users and testers.
  
  
(If your name is missing here - sorry. 
 Just remind me to add it!)



