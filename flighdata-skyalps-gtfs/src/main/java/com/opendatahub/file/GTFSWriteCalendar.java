// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.file;

import java.io.FileWriter;
import java.util.List;

import com.opendatahub.gtfs.CalendarValues;

public class GTFSWriteCalendar {
	public static void writeCalendar(List<CalendarValues> calendarValuesList) throws Exception {

		String firstLine = "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date";

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getCalendar());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));

		for (CalendarValues cal : calendarValuesList) {
			writer.write(cal.getService_id() + ",");
			writer.write(cal.getMonday() + ",");
			writer.write(cal.getTuesday() + ",");
			writer.write(cal.getWednesday() + ",");
			writer.write(cal.getThursday() + ",");
			writer.write(cal.getFriday() + ",");
			writer.write(cal.getSaturday() + ",");
			writer.write(cal.getSunday() + ",");
			writer.write(cal.getStart_date() + ",");
			writer.write(cal.getEnd_date());
			writer.write(System.getProperty("line.separator"));
		}
		writer.close();
	}
}
