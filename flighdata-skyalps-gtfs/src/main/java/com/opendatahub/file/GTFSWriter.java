// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.file;

import java.io.File;
import java.io.PrintWriter;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

import com.opendatahub.gtfs.AgencyValues;
import com.opendatahub.gtfs.CalendarValues;
import com.opendatahub.gtfs.Calendar_DatesValues;
import com.opendatahub.gtfs.FeedInfoValue;
import com.opendatahub.gtfs.RoutesValues;
import com.opendatahub.gtfs.ShapeValue;
import com.opendatahub.gtfs.Stop_TimesValues;
import com.opendatahub.gtfs.StopsValue;
import com.opendatahub.gtfs.TripsValues;

public class GTFSWriter {
	public static final File FOLDER_FILE = new File("GTFS");

	public static String ZIP_FILE_NAME = FOLDER_FILE + ".zip";

	public static void makeFolder() throws Exception {
		if (!FOLDER_FILE.exists()) {
			FOLDER_FILE.mkdirs();
		}
	}

	private static List<String[]> newCsv() {
		return new ArrayList<>();
	}

	private static void addRow(List<String[]> l, String... vs) {
		l.add(vs);
	};

	private static void writeCsv(String file, List<String[]> csv) throws Exception {
		try (PrintWriter pw = new PrintWriter(FOLDER_FILE.getAbsolutePath() + "/" + file)) {
			csv.stream()
					.map(r -> String.join(",", r))
					.forEach(pw::println);
		}
	}

	public static void writeStop_Times(List<Stop_TimesValues> stopTimesValues) throws Exception {
		var csv = newCsv();
		addRow(csv, "trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence", "timepoint",
				"shape_dist_traveled");
		for (var stoptimesvalues : stopTimesValues) {
			addRow(csv,
					stoptimesvalues.trip_id(),
					// well, not nice, but this solves the needed formatting of HH:MM:SS
					stoptimesvalues.arrival_time() + ":00",
					stoptimesvalues.departure_time() + ":00",
					stoptimesvalues.stop_id(),
					String.valueOf(stoptimesvalues.stop_sequence()),
					String.valueOf(stoptimesvalues.timepoint().value),
					stoptimesvalues.shape_dist_traveled());
		}
		writeCsv("stop_times.txt", csv);
	}

	public static void writeAgency(List<AgencyValues> agencyvalueslist) throws Exception {
		var csv = newCsv();
		addRow(csv, "agency_id", "agency_name", "agency_url", "agency_timezone");

		Set<AgencyValues> uniqueAgencies = new HashSet<>(agencyvalueslist);

		for (AgencyValues agency : uniqueAgencies) {
			addRow(csv,
					agency.agency_name(),
					agency.agency_id(),
					agency.agency_url().toString(),
					agency.agency_timezone());
		}
		writeCsv("agency.txt", csv);
	}

	public static void writeCalendar_Dates(List<Calendar_DatesValues> calendarValuesList) throws Exception {
		var csv = newCsv();
		addRow(csv, "service_id", "date", "exception_type");
		writeCsv("calendar_dates.txt", csv);
	}

	public static void writeCalendar(List<CalendarValues> calendarValuesList) throws Exception {
		var csv = newCsv();
		addRow(csv, "service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
				"start_date", "end_date");

		for (CalendarValues cal : calendarValuesList) {
			addRow(csv,
					cal.getService_id(),
					String.valueOf(cal.getMonday()),
					String.valueOf(cal.getTuesday()),
					String.valueOf(cal.getWednesday()),
					String.valueOf(cal.getThursday()),
					String.valueOf(cal.getFriday()),
					String.valueOf(cal.getSaturday()),
					String.valueOf(cal.getSunday()),
					cal.getStart_date(),
					cal.getEnd_date());
		}
		writeCsv("calendar.txt", csv);
	}

	public static void writeRoutes(List<RoutesValues> routesValueslist) throws Exception {
		var csv = newCsv();
		addRow(csv, "route_id", "route_short_name", "route_type", "agency_id");

		Set<RoutesValues> uniqueRoutes = new HashSet<>(routesValueslist);
		for (RoutesValues route : uniqueRoutes) {
			addRow(csv,
					route.route_id(),
					route.route_short_name().toString(),
					String.valueOf(route.route_type()),
					route.agency_id());
		}
		writeCsv("routes.txt", csv);
	}

	public static void writeStops(List<StopsValue> stopsvalues) throws Exception {
		var csv = newCsv();
		addRow(csv, "stop_id", "stop_code", "stop_name", "stop_lat", "stop_lon");

		Set<StopsValue> uniqueStops = new HashSet<>(stopsvalues);

		for (StopsValue stop : uniqueStops) {
			addRow(csv,
					stop.stop_id(),
					stop.stop_code(),
					stop.stop_name().toString(),
					stop.stop_lat(),
					stop.stop_lon());
		}
		writeCsv("stops.txt", csv);
	}

	public static void writeTrips(List<TripsValues> tripsvalueslist) throws Exception {
		var csv = newCsv();
		addRow(csv, "route_id", "service_id", "trip_id", "shape_id");

		for (TripsValues tripsvalues : tripsvalueslist) {
			addRow(csv,
					tripsvalues.route_id(),
					tripsvalues.service_id(),
					tripsvalues.trip_id(),
					tripsvalues.shape_id());
		}
		writeCsv("trips.txt", csv);
	}

	public static void writeFeedInfo(List<FeedInfoValue> feedInfos) throws Exception {
		var csv = newCsv();
		addRow(csv, " feed_publisher_name", "feed_publisher_url", "feed_lang");

		for (FeedInfoValue feed : feedInfos) {
			addRow(csv,
					feed.feed_publisher_name(),
					feed.feed_publisher_url(),
					feed.feed_lang());
		}
		writeCsv("feed_info.txt", csv);
	}

	public static void writeShape(List<ShapeValue> shapes) throws Exception {
		var csv = newCsv();
		addRow(csv, " shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence", "shape_dist_traveled");

		shapes.stream()
				// shapes unique per ID/sequence
				.collect(Collectors.toConcurrentMap(
						s -> Collections.unmodifiableList(Arrays.asList(s.shape_id(), s.shape_pt_sequence())),
						Function.identity(),
						(l, r) -> l))
				.values().stream()
				.sorted(Comparator
						.comparing(ShapeValue::shape_id)
						.thenComparing(ShapeValue::shape_pt_sequence))
				.forEach((shape) -> addRow(csv,
						shape.shape_id(),
						shape.shape_pt_lat(),
						shape.shape_pt_lon(),
						String.valueOf(shape.shape_pt_sequence()),
						shape.shape_dist_traveled()));

		writeCsv("shape.txt", csv);
	}
}
