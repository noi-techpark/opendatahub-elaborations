package it.noitechpark.service;

import java.io.FileWriter;

import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;

import it.noitechpark.constantsClasses.Routes;
import it.noitechpark.dto.RoutesValues;

public class GTFSWriteRoutes {
	public static void writeRoutes(ArrayList<RoutesValues> routesValueslist) throws IOException, MalformedURLException, GTFSCheckRoutes, GTFSCheckStops {

		Routes routes = new Routes();

		String firstLine = routes.getRoute_id() + "," + routes.getAgency_id() + "," + routes.getRoute_short_name() + ","
				+ routes.getRoute_long_name() + "," + routes.getRoute_desc() + "," + routes.getRoute_type() + ","
				+ routes.getRoute_URL() + "," + routes.getRoute_colour() + "," + routes.getRoute_text_color() + ","
				+ routes.getRoute_sort_order() + "," + routes.getContinous_pickup() + ","
				+ routes.getContinous_drop_off();

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getRoutes());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		RoutesValues routesvalues = new RoutesValues();
		if(GTFSCheckRoutes.checkRoutesMandatoryFields(routesValueslist) && GTFSCheckRoutes.checkagencyid(routesValueslist) && GTFSCheckRoutes.checkrouteshortandlongname(routesValueslist)) {
		for (int i = 0; i < routesValueslist.size(); i++) {
			routesvalues.setRoute_id(routesValueslist.get(i).getRoute_id());
			routesvalues.setAgency_id(routesValueslist.get(i).getAgency_id());
			routesvalues.setRoute_short_name(routesValueslist.get(i).getRoute_short_name());
			routesvalues.setRoute_URL(routesValueslist.get(i).getRoute_URL());
			routesvalues.setRoute_desc(routesValueslist.get(i).getRoute_desc());
			routesvalues.setRoute_type(routesValueslist.get(i).getRoute_type());
			routesvalues.setRoute_URL(routesValueslist.get(i).getRoute_URL());
			routesvalues.setRoute_color(routesValueslist.get(i).getRoute_color());

			routesvalues.setRoute_text_color(routesValueslist.get(i).getRoute_text_color());
			routesvalues.setRoute_sort_order(routesValueslist.get(i).getRoute_sort_order());
			routesvalues.setContinous_pickup(routesValueslist.get(i).getContinous_pickup());
			routesvalues.setContinous_drop_off(routesValueslist.get(i).getContinous_drop_off());
			writer.write(routesvalues.getRoute_id() + ",");
			writer.write(routesvalues.getAgency_id() + ",");
			writer.write(routesvalues.getRoute_short_name().toString() + ",");
			writer.write(routesvalues.getRoute_long_name() + ",");
			writer.write(routesvalues.getRoute_desc().toString() + ",");
			writer.write(routesvalues.getRoute_type() + ",");
			writer.write(routesvalues.getRoute_URL().toExternalForm() + ",");
			writer.write(routesvalues.getRoute_color().toString() + ",");
			writer.write(routesvalues.getRoute_text_color().toString() + ",");
			writer.write(routesvalues.getRoute_sort_order() + ",");
			writer.write(routesvalues.getContinous_pickup().toString() + ",");
			writer.write(routes.getContinous_drop_off().toString());
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
