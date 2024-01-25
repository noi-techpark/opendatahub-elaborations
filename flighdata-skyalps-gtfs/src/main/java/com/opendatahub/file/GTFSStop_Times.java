// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.file;

import java.io.FileWriter;
import java.util.ArrayList;

import com.opendatahub.gtfs.Stop_TimesValues;

public class GTFSStop_Times {

	public static void writeStop_Times(ArrayList<Stop_TimesValues> stopTimesValues) throws Exception { 
		String firstLine = "trip_id,arrival_time,departure_time,stop_id,stop_sequence,timepoint";

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getStop_Times());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		for (var stoptimesvalues : stopTimesValues) {
			writer.write(stoptimesvalues.trip_id() + ",");
			// well, not nice, but this solves the needed formatting of HH:MM:SS
			writer.write(stoptimesvalues.arrival_time() + ":00" + ",");
			writer.write(stoptimesvalues.departure_time() + ":00" + ",");
			writer.write(stoptimesvalues.stop_id().toString() + ",");
			writer.write(String.valueOf(stoptimesvalues.stop_sequence()) + ",");
			writer.write(String.valueOf(stoptimesvalues.timepoint().value));
			writer.write(System.getProperty("line.separator"));
		}
		writer.close();
	}
}
