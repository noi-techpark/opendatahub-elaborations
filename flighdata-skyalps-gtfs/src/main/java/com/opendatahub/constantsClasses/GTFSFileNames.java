// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.constantsClasses;

public class GTFSFileNames {

	private static String agency = "Agency";
	private static String stops = "Stops";
	private static String routes = "Routes";
	private static String trips = "Trips";
	private static String stop_times = "Stop_times";
	private static String calendar = "Calendar";
	private static String calendar_dates = "Calendar_dates";
	private static String fare_attributes = "Fare_attributes";
	private static String fare_rules = "Fare_rules";
	private static String shapes = "Shapes";
	private static String frequencies = "Frequencies";
	private static String transfers = "Transfers";
	private static String feed_info = "Feed_info";

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
