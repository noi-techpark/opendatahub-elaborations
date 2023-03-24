package it.noitechpark;

import java.io.IOException;

import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;

import org.json.JSONArray;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

import com.opendatahub.validation.CheckLocationType;
import com.opendatahub.constantsClasses.DefaultValues;
import com.opendatahub.dto.AgencyValues;
import com.opendatahub.dto.CalendarValues;
import com.opendatahub.dto.Calendar_DatesValues;
import com.opendatahub.dto.Flights;
import com.opendatahub.dto.RoutesValues;
import com.opendatahub.dto.Stop_TimesValues;
import com.opendatahub.dto.StopsValue;
import com.opendatahub.dto.TripsValues;
import com.opendatahub.enumClasses.bikes_allowed;
import com.opendatahub.enumClasses.continous_drop_off;
import com.opendatahub.enumClasses.continous_pickup;
import com.opendatahub.enumClasses.continous_pickup_stopTimes;
import com.opendatahub.enumClasses.location_type;
import com.opendatahub.enumClasses.parentless_stops;
import com.opendatahub.enumClasses.pickup_type;
import com.opendatahub.enumClasses.route_color;
import com.opendatahub.enumClasses.route_type;
import com.opendatahub.enumClasses.service_operation;
import com.opendatahub.enumClasses.stop_sequence;
import com.opendatahub.enumClasses.timepoint;
import com.opendatahub.enumClasses.wheelchair_accessible;
import com.opendatahub.interfaceClasses.wheelchair_boarding;
import com.opendatahub.rest.FlightsRest;
import com.opendatahub.service.GTFSCheckStops;
import com.opendatahub.service.GTFSFile;
import com.opendatahub.service.GTFSFolder;
import com.opendatahub.service.GTFSStop_Times;
import com.opendatahub.service.GTFSWriteAgency;
import com.opendatahub.service.GTFSWriteCalendar;
import com.opendatahub.service.GTFSWriteCalendar_Dates;
import com.opendatahub.service.GTFSWriteRoutes;
import com.opendatahub.service.GTFSWriteStops;
import com.opendatahub.service.GTFSWriteTrips;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;

@SpringBootApplication
public class SkyAlpsApplication implements CommandLineRunner {

	private static final Logger LOG = LoggerFactory.getLogger(SkyAlpsApplication.class);
	@Autowired
	private RestTemplate restTemplate;

	@Autowired
	GTFSFolder gtfsfolder;

	@Bean(name = "appRestClient")
	public static RestTemplate getRestClient() {
		RestTemplate restClient = new RestTemplate();
		restClient.setInterceptors(Collections.singletonList((request, body, execution) -> {
			LOG.debug("Intercepting...");
			return execution.execute(request, body);
		}));
		return restClient;
	}

	public static void main(String[] args) {
		SpringApplication.run(SkyAlpsApplication.class, args);

	}

	@Bean
	public CommandLineRunner run(RestTemplate restTemplate)
			throws Exception, JsonParseException, JsonMappingException, IOException {
		return args -> {
			Date date = new Date();
			SimpleDateFormat format = new SimpleDateFormat("yyyy_MM_dd_HH.mm.ss");

			String currentDateTime = format.format(date);
			ArrayList<AgencyValues> agencyValues = new ArrayList<AgencyValues>();
			ArrayList<Calendar_DatesValues> calendarDatesValues = new ArrayList<Calendar_DatesValues>();
			ArrayList<CalendarValues> calendarValues = new ArrayList<CalendarValues>();
			ArrayList<Stop_TimesValues> stoptimesvalues = new ArrayList<Stop_TimesValues>();
			ArrayList<TripsValues> tripsvalueslist = new ArrayList<TripsValues>();
			ArrayList<RoutesValues> routesvaluelist = new ArrayList<RoutesValues>();
			ArrayList<StopsValue> stopsvalueslist = new ArrayList<StopsValue>();
			Flights result = FlightsRest.getFlights(restTemplate);
			LOG.info("Result: " + result);

			ObjectMapper objectMapper = new ObjectMapper();
			String json = objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(result.getData()).toString();
			LOG.info("Result Flights: " + json);
			GTFSFolder.writeRequestAndResponse();
			GTFSFile.writeFiles();
			JSONArray json2 = new JSONArray(json);
			List<String> snames = new ArrayList<String>();
			List<String> sorigin = new ArrayList<String>();
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
				}
				if (json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()) != null) {
					// System.out.println(
					// json2.getJSONObject(i).getJSONObject("smetadata").get(String.valueOf(json2.getJSONObject(i).getJSONObject("smetadata"))));
					// System.out.println(json2.getJSONObject(i).getJSONObject("smetadata").getString(json2.getJSONObject(i).getJSONObject("smetadata").toString()));
					weekdayfri.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getBoolean(DefaultValues.getWeekdayfriString()));
					weekdaymon.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getBoolean(DefaultValues.getWeekdaymonString()));
					weekdaysat.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getBoolean(DefaultValues.getWeekdaysatString()));
					weekdaysun.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getBoolean(DefaultValues.getWeekdaysunString()));
					weekdaythu.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getBoolean(DefaultValues.getWeekdaythuString()));
					weekdaytue.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getBoolean(DefaultValues.getWeekdaytueString()));
					weekdaywed.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getBoolean(DefaultValues.getWeekdaywedString()));
				}
				if (json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getString(DefaultValues.getStaString()) != null) {
					sta.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getString(DefaultValues.getStaString()).toString());
				}
				if (json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getString(DefaultValues.getStdString()) != null) {
					std.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getString(DefaultValues.getStdString()).toString());
				}
				if (json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getString(DefaultValues.getTodestinationString()) != null) {
					todestination.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
							.getString(DefaultValues.getTodestinationString()).toString());
				}
				if (json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString()).getString(DefaultValues.getFromdestinationString()) != null) {
					fromdestination.add(json2.getJSONObject(i).getJSONObject(DefaultValues.getSmetadataString())
							.getString(DefaultValues.getFromdestinationString()).toString());
				}
			}
			for (int i = 0; i < sorigin.size(); i++) {
				agencyValues.add(new AgencyValues("1", sorigin.get(i).toString(), null, null, null, null, null, null));
			}
			for (int j = 0; j < stoptimesvalues.size(); j++) {
				LOG.info(stoptimesvalues.get(j).toString());
			}
			for (int i = 0; i < scode.size(); i++) {
				calendarValues.add(new CalendarValues(scode.get(i), service_operation.valueOf(false),
						service_operation.valueOf(false), service_operation.valueOf(false),
						service_operation.valueOf(false), service_operation.valueOf(false),
						service_operation.valueOf(false), currentDateTime, currentDateTime));
				tripsvalueslist
						.add(new TripsValues(null, calendarValues.get(i).getService_id().toString(), scode.get(i), null,
								null, null, null, "2", wheelchair_accessible.valueOf(1), bikes_allowed.valueOf(1)));
			}
			for (int i = 0; i < sta.size(); i++) {
				stoptimesvalues.add(new Stop_TimesValues(DefaultValues.getStaticTripID(), sta.get(i), DefaultValues.getStaticStopID(), "null",
						stop_sequence.valueOf(1), null, pickup_type.valueOf(1), pickup_type.valueOf(0),
						continous_pickup_stopTimes.valueOf(1), continous_pickup_stopTimes.valueOf(2), 12,
						timepoint.valueOf(1)));
				tripsvalueslist.get(i).setDirection_id(sta.get(i));
			}

			for (int i = 0; i < std.size(); i++) {
				for (int j = 0; j < stoptimesvalues.size(); j++) {
					stoptimesvalues.get(j).setDeparture_time(std.get(i));
				}
			}
			for (int i = 0; i < weekdayfri.size(); i++) {
				for (int j = 0; j < calendarValues.size(); j++) {
					calendarValues.get(j).setFriday(service_operation.valueOf(weekdayfri.get(i)));
				}
			}
			for (int i = 0; i < weekdaymon.size(); i++) {
				for (int j = 0; j < calendarValues.size(); j++) {
					calendarValues.get(j).setFriday(service_operation.valueOf(weekdaymon.get(i)));
				}
			}
			for (int i = 0; i < weekdaythu.size(); i++) {
				for (int j = 0; j < calendarValues.size(); j++) {
					calendarValues.get(j).setFriday(service_operation.valueOf(weekdaythu.get(i)));
				}
			}
			for (int i = 0; i < weekdaysat.size(); i++) {
				for (int j = 0; j < calendarValues.size(); j++) {
					calendarValues.get(j).setFriday(service_operation.valueOf(weekdaysat.get(i)));
				}
			}
			for (int i = 0; i < weekdaysun.size(); i++) {
				for (int j = 0; j < calendarValues.size(); j++) {
					calendarValues.get(j).setFriday(service_operation.valueOf(weekdaysun.get(i)));
				}
			}
			for (int i = 0; i < weekdaytue.size(); i++) {
				for (int j = 0; j < calendarValues.size(); j++) {
					calendarValues.get(j).setFriday(service_operation.valueOf(weekdaytue.get(i)));
				}
			}
			for (int i = 0; i < weekdaywed.size(); i++) {
				for (int j = 0; j < calendarValues.size(); j++) {
					calendarValues.get(j).setFriday(service_operation.valueOf(weekdaywed.get(i)));
				}
			}
			for (int i = 0; i < todestination.size(); i++) {
				routesvaluelist.add(new RoutesValues(todestination.get(i), agencyValues.get(i).getAgency_id(),
						todestination.get(i), DefaultValues.getRouteShortLongName(), DefaultValues.getRouteShortLongName(), route_type.valueOf(1),
						new URL(DefaultValues.getDefultAgency_urlValue()), route_color.valueOf(1), route_color.valueOf(1), 1,
						continous_pickup.valueOf(1), continous_drop_off.valueOf(1)));
				stopsvalueslist.add(new StopsValue(todestination.get(i), todestination.get(i), todestination.get(i),
						null, null, null, null, null, new URL(DefaultValues.getDefultAgency_urlValue()), location_type.valueOf(1), 1, null,
						wheelchair_boarding.getparentlessstops(2), null, "1"));
				tripsvalueslist.get(i).setRoute_id(todestination.get(i));
			}
			for (int i = 0; i < fromdestination.size(); i++) {
				stopsvalueslist.add(new StopsValue(fromdestination.get(i), fromdestination.get(i),
						fromdestination.get(i), null, null, null, null, null, new URL(DefaultValues.getDefultAgency_urlValue()),
						location_type.valueOf(1), 1, null, parentless_stops.valueOf(1), null, "1"));
				routesvaluelist.add(new RoutesValues(fromdestination.get(i), agencyValues.get(i).getAgency_id(),
						fromdestination.get(i), DefaultValues.getRouteShortLongName(), DefaultValues.getRouteShortLongName(), route_type.valueOf(1),
						new URL(DefaultValues.getDefultAgency_urlValue()), route_color.valueOf(1), route_color.valueOf(1), 1,
						continous_pickup.valueOf(1), continous_drop_off.valueOf(1)));

			}
			
			GTFSWriteAgency.writeAgency(agencyValues);
			GTFSWriteCalendar_Dates.writeCalendar_Dates(calendarDatesValues);
			GTFSStop_Times.writeStop_Times(stoptimesvalues);
			GTFSWriteCalendar.writeCalendar(calendarValues);
			GTFSWriteStops.writeStops(stopsvalueslist);
			GTFSWriteRoutes.writeRoutes(routesvaluelist);

			GTFSWriteTrips.writeTrips(tripsvalueslist);
			/*
			 * JSONObject json2_obj = json2.getJSONObject(2); Gson gson = new
			 * GsonBuilder().setPrettyPrinting().create(); String json2_obj_pretty =
			 * gson.toJson(json2_obj); String sname = json2_obj.getString("sname");
			 * System.out.println(sname);
			 */
		};

	}

	@Override
	public void run(String... args) throws Exception {
		// TODO Auto-generated method stub

	}

}