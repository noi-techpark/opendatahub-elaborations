// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.file;

import java.io.FileWriter;
import java.util.ArrayList;

import com.opendatahub.gtfs.Calendar_DatesValues;

public class GTFSWriteCalendar_Dates {
	public static void writeCalendar_Dates(ArrayList<Calendar_DatesValues> calendarValuesList) throws Exception {
		String firstLine = "service_id,date,exception_type";

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getCalendar_Dates());
		writer.write(firstLine);
		writer.close();
	}
}
