// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

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

		// String firstLine = trips.getRoute_id() + "," + trips.getService_id() + "," + trips.getTrip_id() + "," + trips.getDirection_id();
		String firstLine = trips.getRoute_id() + "," + trips.getService_id() + "," + trips.getTrip_id(); // remove direction_id 


		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getTrips());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		TripsValues tripsvalues = new TripsValues();
		if(GTFSCheckTrips.checkTripsMandatoryFields(tripsvalueslist)) {
		for (int i = 0; i < tripsvalueslist.size(); i++) {
			tripsvalues.setRoute_id(tripsvalueslist.get(i).getRoute_id());
			tripsvalues.setService_id(tripsvalueslist.get(i).getService_id());
			tripsvalues.setTrip_id(tripsvalueslist.get(i).getTrip_id());
			tripsvalues.setDirection_id(tripsvalueslist.get(i).getDirection_id());
			writer.write(tripsvalues.getRoute_id() + ",");
			writer.write(tripsvalues.getService_id() + ",");
			writer.write(tripsvalues.getTrip_id().toString());
			// writer.write(String.valueOf(tripsvalues.getDirection_id()).toString());
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
