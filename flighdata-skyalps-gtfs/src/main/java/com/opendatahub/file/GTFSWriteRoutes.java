// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.file;

import java.io.FileWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

import com.opendatahub.gtfs.RoutesValues;

public class GTFSWriteRoutes {
	public static void writeRoutes(ArrayList<RoutesValues> routesValueslist) throws Exception {
		String firstLine = "route_id,route_short_name,route_type,agency_id";

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getRoutes());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));

		Set<RoutesValues> uniqueRoutes = new HashSet<>(routesValueslist);
		for (RoutesValues route : uniqueRoutes) {
			writer.write(route.route_id() + ",");
			writer.write(route.route_short_name().toString() + ",");
			writer.write(String.valueOf(route.route_type()) + ",");
			writer.write(route.agency_id());
			writer.write(System.getProperty("line.separator"));
		}
		writer.close();
	}
}
