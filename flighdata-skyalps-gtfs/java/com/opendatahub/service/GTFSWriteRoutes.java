package com.opendatahub.service;

import java.io.FileWriter;

import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;

import com.opendatahub.constantsClasses.Routes;
import com.opendatahub.dto.RoutesValues;

public class GTFSWriteRoutes {
	public static void writeRoutes(ArrayList<RoutesValues> routesValueslist) throws IOException, MalformedURLException, GTFSCheckRoutes, GTFSCheckStops {

		Routes routes = new Routes();

		String firstLine = routes.getRoute_id() + "," + routes.getRoute_short_name() + "," + routes.getRoute_type() + ",";

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getRoutes());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		RoutesValues routesvalues = new RoutesValues();
		if(GTFSCheckRoutes.checkRoutesMandatoryFields(routesValueslist)) {
		for (int i = 0; i < routesValueslist.size(); i++) {
			routesvalues.setRoute_id(routesValueslist.get(i).getRoute_id());
			routesvalues.setRoute_short_name(routesValueslist.get(i).getRoute_short_name());
			routesvalues.setRoute_type(routesValueslist.get(i).getRoute_type());
			writer.write(routesvalues.getRoute_id() + ",");
			writer.write(routesvalues.getRoute_short_name().toString() + ",");
			writer.write(String.valueOf(routesvalues.getRoute_type()));
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
