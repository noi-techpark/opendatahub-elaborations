// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.file;

import java.io.FileWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

import com.opendatahub.gtfs.StopsValue;

public class GTFSWriteStops {

	public static void writeStops(ArrayList<StopsValue> stopsvalues) throws Exception {
		String firstLine = "stop_id,stop_code,stop_name,stop_lat,stop_lon";

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getStops());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		Set<StopsValue> uniqueStops = new HashSet<>(stopsvalues);

		for (StopsValue stop : uniqueStops) {
			writer.write(stop.stop_id() + ",");
			writer.write(stop.stop_code() + ",");
			writer.write(stop.stop_name().toString() + ",");
			writer.write(String.valueOf(stop.stop_lat()) + ",");
			writer.write(String.valueOf(stop.stop_lon()));
			writer.write(System.getProperty("line.separator"));
		}
		writer.close();
	}
}
