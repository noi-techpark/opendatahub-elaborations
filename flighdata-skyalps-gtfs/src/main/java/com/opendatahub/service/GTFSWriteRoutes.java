// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.service;

import java.io.FileWriter;

import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.opendatahub.constantsClasses.Routes;
import com.opendatahub.dto.RoutesValues;

public class GTFSWriteRoutes {
	public static void writeRoutes(ArrayList<RoutesValues> routesValueslist)
			throws IOException, MalformedURLException, GTFSCheckRoutes, GTFSCheckStops {

		Routes routes = new Routes();

		String firstLine = routes.getRoute_id() + "," + routes.getRoute_short_name() + "," + routes.getRoute_type()
				+ ",";

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getRoutes());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		RoutesValues routesvalues = new RoutesValues();
		if (GTFSCheckRoutes.checkRoutesMandatoryFields(routesValueslist)) {
			// System.out.println("Before removing duplicates : " + Arrays.toString(routesValueslist.toArray()));

			final List<RoutesValues> listWithoutDuplicates = new ArrayList<>(
					new HashSet<>(routesValueslist));

			Set<RoutesValues> uniqueRoutes = new HashSet<>(routesValueslist);

			// System.out.println("After removing duplicates :: "
			// + Arrays.toString(routesValueslist.toArray()));

			for (RoutesValues routes2 : uniqueRoutes) {
				/*
				 * routesvalues.setRoute_id(routesValueslist.get(i).getRoute_id());
				 * routesvalues.setRoute_short_name(routesValueslist.get(i).getRoute_short_name(
				 * ));
				 * routesvalues.setRoute_type(routesValueslist.get(i).getRoute_type());
				 */
				writer.write(routes2.getRoute_id() + ",");
				writer.write(routes2.getRoute_short_name().toString() + ",");
				writer.write(String.valueOf(routes2.getRoute_type()));
				writer.write(System.getProperty("line.separator"));

			}
			writer.close();
		}
	}

	private static void writeRoutes() {
		// TODO Auto-generated method stub

	}

	public static void main(String[] args) throws IOException {
		writeRoutes();
	}

}
