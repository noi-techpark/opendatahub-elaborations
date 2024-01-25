// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.file;

import java.io.FileWriter;
import java.util.ArrayList;

import com.opendatahub.gtfs.TripsValues;

public class GTFSWriteTrips {
	public static void writeTrips(ArrayList<TripsValues> tripsvalueslist) throws Exception {
		String firstLine = "route_id,service_id,trip_id";

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getTrips());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		for (TripsValues tripsvalues : tripsvalueslist) {
			writer.write(tripsvalues.route_id() + ",");
			writer.write(tripsvalues.service_id() + ",");
			writer.write(tripsvalues.trip_id().toString());
			writer.write(System.getProperty("line.separator"));
		}
		writer.close();
	}
}
