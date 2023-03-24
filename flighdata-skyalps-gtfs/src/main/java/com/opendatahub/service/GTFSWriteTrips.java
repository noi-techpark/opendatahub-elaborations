package com.opendatahub.service;

import java.io.FileWriter;

import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;

import com.opendatahub.constantsClasses.Trips;
import com.opendatahub.dto.TripsValues;

public class GTFSWriteTrips {
	public static void writeTrips(ArrayList<TripsValues> tripsvalueslist) throws IOException, MalformedURLException, GTFSCheckTrips {

		Trips trips = new Trips();

		String firstLine = trips.getRoute_id() + "," + trips.getService_id() + "," + trips.getTrip_id() + ","
				+ trips.getTrip_headsign() + "," + trips.getTrip_short_name() + "," + trips.getDirection_id() + ","
				+ trips.getBlock_id() + "," + trips.getShape_id() + "," + trips.getWheelchair_accessible() + ","
				+ trips.getBikes_allowed();

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getTrips());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		TripsValues tripsvalues = new TripsValues();
		if(GTFSCheckTrips.checkTripsMandatoryFields(tripsvalueslist) && GTFSCheckTrips.checkshapeid(tripsvalueslist)) {
		for (int i = 0; i < tripsvalueslist.size(); i++) {
			tripsvalues.setRoute_id(tripsvalueslist.get(i).getRoute_id());
			tripsvalues.setService_id(tripsvalueslist.get(i).getService_id());
			tripsvalues.setTrip_id(tripsvalueslist.get(i).getTrip_id());
			tripsvalues.setTrip_headsign(tripsvalueslist.get(i).getTrip_headsign());
			tripsvalues.setTrip_short_name(tripsvalueslist.get(i).getTrip_short_name());
			tripsvalues.setBlock_id(tripsvalueslist.get(i).getBlock_id());
			tripsvalues.setShape_id(tripsvalueslist.get(i).getShape_id());
			tripsvalues.setWheelchair_accessible(tripsvalueslist.get(i).getWheelchair_accessible());
			tripsvalues.setBikes_allowed(tripsvalueslist.get(i).getBikes_allowed());
			writer.write(tripsvalues.getRoute_id() + ",");
			writer.write(tripsvalues.getService_id() + ",");
			writer.write(tripsvalues.getTrip_id().toString() + ",");
			writer.write(tripsvalues.getTrip_headsign() + ",");
			writer.write(tripsvalues.getTrip_short_name() + ",");
			writer.write(tripsvalues.getBlock_id() + ",");
			writer.write(tripsvalues.getShape_id() + ",");
			writer.write(tripsvalues.getWheelchair_accessible().toString());
			writer.write(tripsvalues.getBikes_allowed().toString());
			writer.write(System.getProperty("line.separator"));

		}
		writer.close();
		}
	}

	private static void writeTrips() {
		// TODO Auto-generated method stub

	}

	public static void main(String[] args) throws IOException {
		writeTrips();
	}
}
