// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.constants;

public class GTFSFileNames {

	private static String agency = "agency";
	private static String stops = "stops";
	private static String routes = "routes";
	private static String trips = "trips";
	private static String stop_times = "stop_times";
	private static String calendar = "calendar";
	private static String calendar_dates = "calendar_dates";
	private static String fare_attributes = "fare_attributes";
	private static String fare_rules = "fare_rules";
	private static String shapes = "shapes";
	private static String frequencies = "frequencies";
	private static String transfers = "transfers";
	private static String feed_info = "feed_info";

	public String getAgency() {
		return agency;
	}

	public String getStops() {
		return stops;
	}

	public String getRoutes() {
		return routes;
	}

	public String getTrips() {
		return trips;
	}

	public String getStop_times() {
		return stop_times;
	}

	public String getCalendar() {
		return calendar;
	}

	public String getCalendar_dates() {
		return calendar_dates;
	}

	public String getFare_attributes() {
		return fare_attributes;
	}

	public String getFare_rules() {
		return fare_rules;
	}

	public String getShapes() {
		return shapes;
	}

	public String getFrequencies() {
		return frequencies;
	}

	public String getTransfers() {
		return transfers;
	}

	public String getFeed_info() {
		return feed_info;
	}

	@Override
	public String toString() {
		return "GTFSFileNames [agency=" + agency + ", stops=" + stops + ", routes=" + routes + ", trips=" + trips
				+ ", stop_times=" + stop_times + ", calendar=" + calendar + ", calendar_dates=" + calendar_dates
				+ ", fare_attributes=" + fare_attributes + ", fare_rules=" + fare_rules + ", shapes=" + shapes
				+ ", frequencies=" + frequencies + ", transfers=" + transfers + ", feed_info=" + feed_info + "]";
	}

}
