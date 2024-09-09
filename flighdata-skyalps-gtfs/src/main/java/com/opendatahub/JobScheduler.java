// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TimeZone;
import java.util.function.Function;
import java.util.stream.Collector;
import java.util.stream.Collectors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.opendatahub.constants.SkyalpsAgency;
import com.opendatahub.dto.Data;
import com.opendatahub.dto.Flights;
import com.opendatahub.file.AirportCoordinates;
import com.opendatahub.file.GTFSWriter;
import com.opendatahub.gtfs.AgencyValues;
import com.opendatahub.gtfs.CalendarValues;
import com.opendatahub.gtfs.Calendar_DatesValues;
import com.opendatahub.gtfs.FeedInfoValue;
import com.opendatahub.gtfs.RoutesValues;
import com.opendatahub.gtfs.ShapeValue;
import com.opendatahub.gtfs.Stop_TimesValues;
import com.opendatahub.gtfs.StopsValue;
import com.opendatahub.gtfs.Timepoint;
import com.opendatahub.gtfs.TripsValues;

import jakarta.annotation.PostConstruct;

@Service
public class JobScheduler {

    private static final Logger LOG = LoggerFactory.getLogger(JobScheduler.class);

	private static final DecimalFormat twoDecimals = new DecimalFormat("0.00");

    @Autowired
    private S3FileUtil s3FileUtil;

    @Autowired
    private AirportCoordinates gtfsCsvFile;

    @Autowired
    private FlightsRest flightsRest;

    @PostConstruct
    private void postConstruct() throws JsonParseException, JsonMappingException, IOException, Exception {
        // calc on time on startup
        calculateGtfs();
    }
    
    private record Week(boolean mon, boolean tue, boolean wed, boolean thu, boolean fri, boolean sat, boolean sun) {};

    private static class Flight {
        String name;
        String id;
        String origin;
        String code;
        String fullCode;
        String arrivalTime;
        String departureTime;
        Week week;
        String toDestination;
        String fromDestination;
    }

    @Scheduled(cron = "${scheduler-cron:*/10 * * * * *}")
    public void calculateGtfs() throws Exception {
        RestTemplate restTemplate = new RestTemplate();

        List<AgencyValues> gtfsAgencies = new ArrayList<>();
        List<Calendar_DatesValues> gtfsCalendarDates = new ArrayList<>();
        Map<String, CalendarValues> gtfsCalendar = new HashMap<>();
        List<Stop_TimesValues> gtfsStopTimes = new ArrayList<>();
        List<TripsValues> gtfsTrips = new ArrayList<>();
        List<RoutesValues> gtfsRoutes = new ArrayList<>();
        List<StopsValue> gtfsStops = new ArrayList<>();
        List<FeedInfoValue> gtfsFeedInfos = new ArrayList<>();
        List<ShapeValue> gtfsShapes = new ArrayList<>();

        Flights flightDtos = flightsRest.getFlights(restTemplate);
        LOG.debug("Result: " + flightDtos);

        GTFSWriter.makeFolder();

        AgencyValues agencySkyalps = new AgencyValues(SkyalpsAgency.agencyName, SkyalpsAgency.agencyName, new URL(SkyalpsAgency.agencyUrl), SkyalpsAgency.agencyTimeZone);
        gtfsAgencies.add(agencySkyalps);
        gtfsFeedInfos.add(new FeedInfoValue(SkyalpsAgency.agencyName, SkyalpsAgency.agencyUrl, "IT"));

        List<Flight> flights = new ArrayList<>();
        
        var airports = gtfsCsvFile.getCSVFile();

        for (Data flightDto : flightDtos.getData()) {
            Flight flight = mapFlightFromJson(flights, flightDto);

            var calendar = mapCalendarValues(flight);
            gtfsCalendar.put(calendar.getService_id(), calendar);
            
            boolean outboundDirection = flight.fromDestination.equals("BZO");
            
            var fromAirport = airports.get(flight.fromDestination);
            if (fromAirport == null) throw new Exception("Airport mapping not found in CSV for IATA code " + flight.fromDestination);
            gtfsStops.add(fromAirport);

            var toAirport = airports.get(flight.toDestination);
            if (toAirport == null) throw new Exception("Airport mapping not found in CSV for IATA code " + flight.toDestination);
            gtfsStops.add(toAirport);

            var airportDist = twoDecimals.format(haversineDist(
                Double.parseDouble(fromAirport.stop_lat()), 
                Double.parseDouble(fromAirport.stop_lon()), 
                Double.parseDouble(toAirport.stop_lat()), 
                Double.parseDouble(toAirport.stop_lon()) 
            ));

            gtfsStopTimes.add(new Stop_TimesValues(
                flight.fullCode, 
                flight.departureTime, 
                flight.departureTime, 
                flight.fromDestination, 
                1,
                Timepoint.exact,
                "0")
            );

            gtfsStopTimes.add(new Stop_TimesValues(
                flight.fullCode, 
                flight.arrivalTime, 
                flight.arrivalTime, 
                flight.toDestination, 
                2,
                Timepoint.exact,
                airportDist)
            );

            var shapeId = flight.id;
            gtfsShapes.add(new ShapeValue(shapeId, fromAirport.stop_lat(), fromAirport.stop_lon(), 1, "0"));
            gtfsShapes.add(new ShapeValue(shapeId, toAirport.stop_lat(), toAirport.stop_lon(), 2, airportDist));

            gtfsTrips.add(new TripsValues(
                flight.id, 
                calendar.getService_id(), 
                flight.fullCode, 
                outboundDirection ? 0 : 1,
                shapeId)
            );

            gtfsRoutes.add(new RoutesValues(flight.id, flight.name, RoutesValues.ROUTE_TYPE_AIR_SERVICE, agencySkyalps.agency_id()));
        }
        
        GTFSWriter.writeAgency(gtfsAgencies);
        GTFSWriter.writeCalendar_Dates(gtfsCalendarDates);
        GTFSWriter.writeStop_Times(gtfsStopTimes);
        GTFSWriter.writeCalendar(List.copyOf(gtfsCalendar.values()));
        GTFSWriter.writeStops(gtfsStops);
        GTFSWriter.writeRoutes(gtfsRoutes);
        GTFSWriter.writeTrips(gtfsTrips);
        GTFSWriter.writeFeedInfo(gtfsFeedInfos);
        GTFSWriter.writeShape(gtfsShapes);

        uploadToS3();
    }
    
    private static double haversineDist(double lat1, double lon1, double lat2, double lon2) {
        double theta = lon1 - lon2;
        double distance = 60 * 1.1515 * (180/Math.PI) * Math.acos(
            Math.sin(lat1 * (Math.PI/180)) * Math.sin(lat2 * (Math.PI/180)) + 
            Math.cos(lat1 * (Math.PI/180)) * Math.cos(lat2 * (Math.PI/180)) * Math.cos(theta * (Math.PI/180))
        );
        return distance * 1.609344;
    }

    private void uploadToS3() throws Exception {
        LOG.info("Uploading files to S3...");

        File[] listFiles = GTFSWriter.FOLDER_FILE.listFiles();

        // create zip file
        File zipFile = new File(GTFSWriter.ZIP_FILE_NAME);
        ZipOutputStream zipOutputStream = new ZipOutputStream(new FileOutputStream(zipFile));

        for (File file : listFiles) {
            LOG.debug("uploading file: {}", file.getName());
            s3FileUtil.uploadFile(file);
            LOG.debug("uploading file done: {}", file.getName());

            // add to zip
            InputStream stream = new FileInputStream(file);
            ZipEntry zipEntry = new ZipEntry(file.getName());
            zipOutputStream.putNextEntry(zipEntry);
            byte[] byteBuffer = new byte[1024];
            int bytesRead = -1;
            while ((bytesRead = stream.read(byteBuffer)) != -1) {
                zipOutputStream.write(byteBuffer, 0, bytesRead);
            }
            stream.close();
            zipOutputStream.flush();
            zipOutputStream.closeEntry();
        }
        zipOutputStream.close();

        LOG.debug("uploading file: {}", zipFile.getName());
        s3FileUtil.uploadFile(zipFile);
        LOG.debug("uploading file done:  {}", zipFile.getName());

        LOG.info("Uploading files to S3 done.");
    }

    private Flight mapFlightFromJson(List<Flight> flights, Data flightDto) {
        Flight flight = new Flight();

        flight.name = flightDto.getSname().replace("-", " - ");
        flight.id = flightDto.getSname().replace("-", "_");

        flight.origin = flightDto.getSorigin();
        flight.fullCode = flightDto.getScode();
        flight.code = flight.fullCode.substring(7);

        var meta = flightDto.getSmetadata();

        flight.week = new Week(
                meta.isWeekdaymon(),
                meta.isWeekdaytue(),
                meta.isWeekdaywed(),
                meta.isWeekdaythu(),
                meta.isWeekdayfri(),
                meta.isWeekdaysat(),
                meta.isWeekdaysun()
        );

        flight.arrivalTime = meta.getSta();
        flight.departureTime = meta.getStd();
        flight.toDestination = meta.getTodestination();
        flight.fromDestination = meta.getFromdestination();
        flights.add(flight);
        return flight;
    }
    
    private CalendarValues mapCalendarValues(Flight flight) throws Exception {
        Date date = new Date();
        SimpleDateFormat format = new SimpleDateFormat("yyyyMMdd");
        String currentDateTime = format.format(date);
        var calValue = new CalendarValues(flight.code, 0, 0, 0, 0, 0, 0, 0, currentDateTime, currentDateTime);
        SimpleDateFormat fromFormat = new SimpleDateFormat("ddMMMyy", Locale.ENGLISH);

        SimpleDateFormat gtfsFormat = new SimpleDateFormat("yyyyMMdd");
        gtfsFormat.setTimeZone(TimeZone.getTimeZone("Italy/Rome"));

        Date sodate = fromFormat.parse(flight.code);

        calValue.setStart_date(gtfsFormat.format(sodate));
        calValue.setEnd_date(gtfsFormat.format(sodate));
        
        Function<Boolean, Integer> btoi = b -> b ? 1 : 0;

        calValue.setMonday(btoi.apply(flight.week.mon));
        calValue.setTuesday(btoi.apply(flight.week.tue));
        calValue.setWednesday(btoi.apply(flight.week.wed));
        calValue.setThursday(btoi.apply(flight.week.thu));
        calValue.setFriday(btoi.apply(flight.week.fri));
        calValue.setSaturday(btoi.apply(flight.week.sat));
        calValue.setSunday(btoi.apply(flight.week.sun));

        return calValue;
    }

}