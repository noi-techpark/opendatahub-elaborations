package com.opendatahub.scheduler;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TimeZone;

import org.json.JSONArray;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.opendatahub.constantsClasses.DefaultValues;
import com.opendatahub.dto.AgencyValues;
import com.opendatahub.dto.CalendarValues;
import com.opendatahub.dto.Calendar_DatesValues;
import com.opendatahub.dto.Flights;
import com.opendatahub.dto.RoutesValues;
import com.opendatahub.dto.Stop_TimesValues;
import com.opendatahub.dto.StopsValue;
import com.opendatahub.dto.TripsValues;
import com.opendatahub.enumClasses.route_type;
import com.opendatahub.enumClasses.service_operation;
import com.opendatahub.enumClasses.stop_sequence;
import com.opendatahub.rest.FlightsRest;
import com.opendatahub.service.GTFSCsvFile;
import com.opendatahub.service.GTFSFile;
import com.opendatahub.service.GTFSFolder;
import com.opendatahub.service.GTFSStop_Times;
import com.opendatahub.service.GTFSWriteAgency;
import com.opendatahub.service.GTFSWriteCalendar;
import com.opendatahub.service.GTFSWriteCalendar_Dates;
import com.opendatahub.service.GTFSWriteRoutes;
import com.opendatahub.service.GTFSWriteStops;
import com.opendatahub.service.GTFSWriteTrips;
import com.opendatahub.utils.S3FileUtil;

@Service
public class JobScheduler {

    private static final Logger LOG = LoggerFactory.getLogger(JobScheduler.class);

    @Autowired
    private GTFSFolder gtfsfolder;

    @Autowired
    private S3FileUtil s3FileUtil;

    @Autowired
    private GTFSCsvFile gtfsCsvFile;

    @Autowired
    private FlightsRest flightsRest;

    @Scheduled(cron = "${scheduler-cron:*/10 * * * * *}")
    public void calculateGtfs()
            throws Exception, JsonParseException, JsonMappingException, IOException {
        RestTemplate restTemplate = new RestTemplate();

        Date date = new Date();
        SimpleDateFormat format = new SimpleDateFormat("yyyyMMdd");

        String currentDateTime = format.format(date);
        ArrayList<AgencyValues> agencyValues = new ArrayList<AgencyValues>();
        ArrayList<Calendar_DatesValues> calendarDatesValues = new ArrayList<Calendar_DatesValues>();
        ArrayList<CalendarValues> calendarValues = new ArrayList<CalendarValues>();
        ArrayList<Stop_TimesValues> stoptimesvalues = new ArrayList<Stop_TimesValues>();
        ArrayList<TripsValues> tripsvalueslist = new ArrayList<TripsValues>();
        ArrayList<RoutesValues> routesvaluelist = new ArrayList<RoutesValues>();
        ArrayList<StopsValue> stopsvalueslist = new ArrayList<StopsValue>();
        Flights result = flightsRest.getFlights(restTemplate);
        LOG.debug("Result: " + result);

        ObjectMapper objectMapper = new ObjectMapper();
        String json = objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(result.getData()).toString();
        LOG.debug("Result Flights: " + json);
        GTFSFolder.writeRequestAndResponse();
        GTFSFile.writeFiles();
        JSONArray json2 = new JSONArray(json);
        List<String> snames = new ArrayList<String>();
        List<String> sorigin = new ArrayList<String>();
        List<String> fullscode = new ArrayList<String>();
        List<String> scode = new ArrayList<String>();
        List<String> sta = new ArrayList<String>();
        List<String> std = new ArrayList<String>();

        List<Boolean> weekdayfri = new ArrayList<Boolean>();
        List<Boolean> weekdaymon = new ArrayList<Boolean>();
        List<Boolean> weekdaysat = new ArrayList<Boolean>();
        List<Boolean> weekdaysun = new ArrayList<Boolean>();
        List<Boolean> weekdaythu = new ArrayList<Boolean>();
        List<Boolean> weekdaytue = new ArrayList<Boolean>();
        List<Boolean> weekdaywed = new ArrayList<Boolean>();

        List<String> todestination = new ArrayList<String>();
        List<String> fromdestination = new ArrayList<String>();
        Map<String, ArrayList<StopsValue>> todestinationHashMap = new HashMap<String, ArrayList<StopsValue>>();
        Map<String, ArrayList<StopsValue>> fromdestinationHashMap = new HashMap<String, ArrayList<StopsValue>>();
        // JSONObject Smetadata = new JSONObject();

        for (int i = 0; i < json2.length(); i++) {
            calendarDatesValues.add(new Calendar_DatesValues(null, null, null));

            if (json2.getJSONObject(i).getString(DefaultValues.getSnameString()) != null) {
                snames.add(json2.getJSONObject(i).get(DefaultValues.getSnameString()).toString());
            }
            if (json2.getJSONObject(i).getString(DefaultValues.getScodeString()) != null) {
                sorigin.add(json2.getJSONObject(i).getString(DefaultValues.getSoriginString()).toString());
            }
            if (json2.getJSONObject(i).getString(DefaultValues.getScodeString()) != null) {
                scode.add(json2.getJSONObject(i).getString(DefaultValues.getScodeString()).substring(7));
                fullscode.add(json2.getJSONObject(i).getString(DefaultValues.getScodeString()));
            }
            if (json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()) != null) {
                // System.out.println(
                // json2.getJSONObject(i).getJSONObject("smetadata").get(String.valueOf(json2.getJSONObject(i).getJSONObject("smetadata"))));
                // System.out.println(json2.getJSONObject(i).getJSONObject("smetadata").getString(json2.getJSONObject(i).getJSONObject("smetadata").toString()));
                weekdayfri.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                        .getBoolean(DefaultValues.getWeekdayfriString()));
                weekdaymon.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                        .getBoolean(DefaultValues.getWeekdaymonString()));
                weekdaysat.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                        .getBoolean(DefaultValues.getWeekdaysatString()));
                weekdaysun.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                        .getBoolean(DefaultValues.getWeekdaysunString()));
                weekdaythu.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                        .getBoolean(DefaultValues.getWeekdaythuString()));
                weekdaytue.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                        .getBoolean(DefaultValues.getWeekdaytueString()));
                weekdaywed.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                        .getBoolean(DefaultValues.getWeekdaywedString()));
            }
            if (json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                    .getString(DefaultValues.getStaString()) != null) {
                sta.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                        .getString(DefaultValues.getStaString()).toString());
            }
            if (json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                    .getString(DefaultValues.getStdString()) != null) {
                std.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                        .getString(DefaultValues.getStdString()).toString());
            }
            if (json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                    .getString(DefaultValues.getTodestinationString()) != null) {
                todestination.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                        .getString(DefaultValues.getTodestinationString()).toString());
            }
            if (json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                    .getString(DefaultValues.getFromdestinationString()) != null) {
                fromdestination.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
                        .getString(DefaultValues.getFromdestinationString()).toString());
            }
        }
        for (int i = 0; i < sorigin.size(); i++) {
            agencyValues.add(new AgencyValues(sorigin.get(i).toString(), null, null));
        }
        for (int j = 0; j < stoptimesvalues.size(); j++) {
            LOG.debug(stoptimesvalues.get(j).toString());
        }
        for (int i = 0; i < scode.size(); i++) {
            calendarValues.add(new CalendarValues(scode.get(i), service_operation.intvalueOf(false),
                    service_operation.intvalueOf(false), service_operation.intvalueOf(false),
                    service_operation.intvalueOf(false), service_operation.intvalueOf(false),
                    service_operation.intvalueOf(false), service_operation.intvalueOf(false), currentDateTime,
                    currentDateTime));
            String scodeDate = scode.get(i).substring(0, 2);
            String scodeMounth = scode.get(i).substring(2, 5);
            if (scodeMounth.equals("JAN")) {
                scodeMounth = "01";
            } else if (scodeMounth.equals("FEB")) {
                scodeMounth = "02";
            } else if (scodeMounth.equals("MAR")) {
                scodeMounth = "03";
            } else if (scodeMounth.equals("APR")) {
                scodeMounth = "04";
            } else if (scodeMounth.equals("MAY")) {
                scodeMounth = "05";
            } else if (scodeMounth.equals("JUN")) {
                scodeMounth = "06";
            } else if (scodeMounth.equals("JUL")) {
                scodeMounth = "07";
            } else if (scodeMounth.equals("AUG")) {
                scodeMounth = "08";
            } else if (scodeMounth.equals("SEP")) {
                scodeMounth = "09";
            } else if (scodeMounth.equals("OCT")) {
                scodeMounth = "10";
            } else if (scodeMounth.equals("NOV")) {
                scodeMounth = "11";
            } else if (scodeMounth.equals("DEC")) {
                scodeMounth = "12";
            }

            String scodeYear = scode.get(i).substring(scode.get(i).length() - 2);
            String fullYear = scodeDate + "/" + scodeMounth + "/" + "20" + scodeYear;
            SimpleDateFormat so = new SimpleDateFormat("dd/MM/yyyy");

            SimpleDateFormat desiredFormat = new SimpleDateFormat("yyyyMMdd");
            desiredFormat.setTimeZone(TimeZone.getTimeZone("Italy/Rome"));

            Date sodate = so.parse(fullYear);
            // System.out.println("DAY : " + desiredFormat.format(sodate));//Questo deve
            // essere flttoperiod per start date e fltsenddate per end date
            calendarValues.get(i).setStart_date(desiredFormat.format(sodate));
            calendarValues.get(i).setEnd_date(desiredFormat.format(sodate));
            tripsvalueslist
                    .add(new TripsValues(null, calendarValues.get(i).getService_id().toString(), scode.get(i),
                            stop_sequence.flightFromBzo()));
        }
        for (int i = 0; i < sta.size(); i++) {
            stoptimesvalues.add(new Stop_TimesValues(DefaultValues.getStaticTripID(), sta.get(i),
                    DefaultValues.getStaticStopID(), "null", stop_sequence.intvalueOf("Departing_airpot")));
            // tripsvalueslist.get(i).setDirection_id(sta.get(i));
        }

        for (int i = 0; i < std.size(); i++) {
            for (int j = 0; j < stoptimesvalues.size(); j++) {
                stoptimesvalues.get(j).setDeparture_time(std.get(i));
            }
        }

        for (int i = 0; i < fullscode.size(); i++) {
            tripsvalueslist.get(i).setTrip_id(fullscode.get(i));
            stoptimesvalues.get(i).setTrip_id(fullscode.get(i));

        }

        /*
         * for (int j = 0; j < calendarValues.size(); j++) {
         * calendarValues.get(j).setMonday(service_operation.intvalueOf(weekdaymon.get(j
         * )));
         * calendarValues.get(j).setFriday(service_operation.intvalueOf(weekdayfri.get(j
         * )));
         * 
         * calendarValues.get(j).setSaturday(service_operation.intvalueOf(weekdaysat.get
         * (j)));
         * calendarValues.get(j).setSunday(service_operation.intvalueOf(weekdaysun.get(j
         * )));
         * calendarValues.get(j).setTuesday(service_operation.intvalueOf(weekdaytue.get(
         * j)));
         * calendarValues.get(j).setWednesday(service_operation.intvalueOf(weekdaywed.
         * get(j)));
         * calendarValues.get(j).setThursday(service_operation.intvalueOf(weekdaythu.get
         * (j)));
         * 
         * }
         */

        for (int j = 0; j < weekdayfri.size() && j < calendarValues.size(); j++) {
            calendarValues.get(j).setFriday(service_operation.intvalueOf(weekdayfri.get(j)));
        }

        for (int j = 0; j < weekdaymon.size() && j < calendarValues.size(); j++) {
            calendarValues.get(j).setMonday(service_operation.intvalueOf(weekdaymon.get(j)));
        }

        for (int j = 0; j < weekdaysat.size() && j < calendarValues.size(); j++) {
            calendarValues.get(j).setSaturday(service_operation.intvalueOf(weekdaysat.get(j)));
        }

        for (int j = 0; j < weekdaysun.size() && j < calendarValues.size(); j++) {
            calendarValues.get(j).setSunday(service_operation.intvalueOf(weekdaysun.get(j)));
        }

        for (int j = 0; j < weekdaythu.size() && j < calendarValues.size(); j++) {
            calendarValues.get(j).setThursday(service_operation.intvalueOf(weekdaythu.get(j)));
        }

        for (int j = 0; j < weekdaytue.size() && j < calendarValues.size(); j++) {
            calendarValues.get(j).setTuesday(service_operation.intvalueOf(weekdaytue.get(j)));
        }

        for (int j = 0; j < weekdaywed.size() && j < calendarValues.size(); j++) {
            calendarValues.get(j).setWednesday(service_operation.intvalueOf(weekdaywed.get(j)));
        }

        for (int i = 0; i < todestination.size(); i++) {
            // routesvaluelist.add(new
            // RoutesValues(todestination.get(i),todestination.get(i),
            // route_type.defaultValue()));
            stopsvalueslist.add(new StopsValue(todestination.get(i), todestination.get(i), todestination.get(i),
                    null, null));
            tripsvalueslist.get(i).setRoute_id(todestination.get(i));
        }

        for (int i = 0; i < fromdestination.size(); i++) {
            stopsvalueslist.add(new StopsValue(fromdestination.get(i), fromdestination.get(i),
                    fromdestination.get(i), null, null));
            // routesvaluelist.add(new
            // RoutesValues(fromdestination.get(i),fromdestination.get(i),
            // route_type.defaultValue()));
            stoptimesvalues.get(i).setStop_id(fromdestination.get(i) + "-" + todestination.get(i));
            if (!fromdestination.get(i).equals("BZO")) {
                stoptimesvalues.get(i).setStop_sequence(1);
                tripsvalueslist.get(i).setDirection_id(stop_sequence.flightToBzo());
            } else {
                stoptimesvalues.get(i).setStop_sequence(2);
                tripsvalueslist.get(i).setDirection_id(stop_sequence.flightFromBzo());
            }

        }
        for (int i = 0; i < stoptimesvalues.size(); i++) {
            stoptimesvalues.get(i).setStop_id(stopsvalueslist.get(i).getStop_id());
        }

        for (int i = 0; i < snames.size(); i++) {
            if (snames.get(i).substring(0, 3).equals("BZO") || snames.get(i).substring(4, 7).equals("BZO")) {
                String newsnames = snames.get(i).replaceAll("-", "_");
                routesvaluelist.add(new RoutesValues(newsnames, newsnames, route_type.defaultValue()));
                tripsvalueslist.get(i).setRoute_id(newsnames);
            }
        }

        for (int i = 0; i < stoptimesvalues.size(); i++) {
            if (stoptimesvalues.get(i).getStop_sequence() == 1) {
                stoptimesvalues.get(i).setArrival_time(std.get(i));
                stoptimesvalues.get(i).setDeparture_time(std.get(i));
            } else if (stoptimesvalues.get(i).getStop_sequence() == 2) {
                stoptimesvalues.get(i).setArrival_time(sta.get(i));
                stoptimesvalues.get(i).setDeparture_time(sta.get(i));
            }
        }
        for (Map.Entry<String, ArrayList<StopsValue>> entry : gtfsCsvFile.getCSVFile().entrySet()) {
            if (todestination.contains(entry.getKey())) {
                String key = entry.getKey();
                ArrayList<StopsValue> value = entry.getValue();
                todestinationHashMap.put(key, value);
            }

        }

        for (Map.Entry<String, ArrayList<StopsValue>> entry : gtfsCsvFile.getCSVFile().entrySet()) {
            if (fromdestination.contains(entry.getKey())) {
                String key = entry.getKey();
                ArrayList<StopsValue> value = entry.getValue();
                fromdestinationHashMap.put(key, value);

            }

        }
        /*
         * for(int i = 0; i < todestination.size(); i++) {
         * for (Map.Entry<String, ArrayList<String[]>> entry :
         * todestinationHashMap.entrySet()) {
         * if(todestination.get(i).equals(entry.getKey())) {
         * ArrayList<String[]> value = entry.getValue();
         * stopsvalueslist.get(i).setStop_lat(value.get(0)[0]);
         * stopsvalueslist.get(i).setStop_lon(value.get(1)[1]);
         * }
         * }
         * }
         */
        for (String destination : todestination) {
            ArrayList<StopsValue> value = todestinationHashMap.get(destination);
            if (value != null && value.size() > 0) {
                StopsValue stop = new StopsValue(value.get(0).getStop_id(), value.get(0).getStop_code(),
                        value.get(0).getStop_name(), value.get(0).getStop_lat(), value.get(0).getStop_lon());
                stopsvalueslist.add(stop);
                // stopsvalueslist.get(0).setStop_lat(value.get(0).getStop_lat()); // pass in
                // the first element of the String array
                // stopsvalueslist.get(0).setStop_lon(value.get(0).getStop_lon()); // pass in
                // the second element of the String array
            }
        }
        Collections.reverse(stopsvalueslist);
        /*
         * for(int i = 0; i < fromdestination.size(); i++) {
         * for (Map.Entry<String, ArrayList<String[]>> entry :
         * fromdestinationHashMap.entrySet()) {
         * if(fromdestination.get(i).equals(entry.getKey())) {
         * ArrayList<String[]> value = entry.getValue();
         * stopsvalueslist.get(i).setStop_lat(value.get(0)[0]);
         * stopsvalueslist.get(i).setStop_lon(value.get(1)[1]);
         * }
         * }
         * }
         */
        for (String destination : fromdestination) {
            ArrayList<StopsValue> value = fromdestinationHashMap.get(destination);
            if (value != null && value.size() > 0) {
                StopsValue stop = new StopsValue(value.get(0).getStop_id(), value.get(0).getStop_code(),
                        value.get(0).getStop_name(), value.get(0).getStop_lat(), value.get(0).getStop_lon());
                stopsvalueslist.add(stop);
                // stopsvalueslist.get(0).setStop_lat(value.get(0).getStop_lat()); // pass in
                // the first element of the String array
                // stopsvalueslist.get(0).setStop_lon(value.get(0).getStop_lon()); // pass in
                // the second element of the String array
            }
        }
        Collections.reverse(stopsvalueslist);

        GTFSWriteAgency.writeAgency(agencyValues);
        GTFSWriteCalendar_Dates.writeCalendar_Dates(calendarDatesValues);
        GTFSStop_Times.writeStop_Times(stoptimesvalues);
        GTFSWriteCalendar.writeCalendar(calendarValues);
        GTFSWriteStops.writeStops(stopsvalueslist);
        GTFSWriteRoutes.writeRoutes(routesvaluelist);
        GTFSWriteTrips.writeTrips(tripsvalueslist);

        /**
         * Upload to S3 bucket
         */
        LOG.info("Uploading files to S3...");

        File[] listFiles = GTFSFolder.FOLDER_FILE.listFiles();

        for (File file : listFiles) {
            LOG.debug("uploading file: {}", file.getName());
            InputStream stream = new FileInputStream(file);
            s3FileUtil.uploadFile(stream, file.getName(), (int) file.length());
            LOG.debug("uploading file done: {}", file.getName());
        }

        LOG.info("Uploading files to S3 done.");
    }

}