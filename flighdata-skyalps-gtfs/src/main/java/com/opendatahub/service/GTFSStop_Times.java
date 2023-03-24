package com.opendatahub.service;

import java.io.FileWriter;

import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;

import com.opendatahub.constantsClasses.Stop_Times;
import com.opendatahub.dto.Stop_TimesValues;

public class GTFSStop_Times {

	public static void writeStop_Times(ArrayList<Stop_TimesValues> stopTimesValues)
			throws IOException, MalformedURLException, GTFSCheckStopTimes {

		Stop_Times stoptimes = new Stop_Times();

		String firstLine = stoptimes.getTrip_id() + "," + stoptimes.getArrival_time() + ","
				+ stoptimes.getDeparture_time() + "," + stoptimes.getStop_id() + "," + stoptimes.getStop_sequence()
				+ "," + stoptimes.getStop_headsign() + "," + stoptimes.getPickup_type() + ","
				+ stoptimes.getDropoff_type() + "," + stoptimes.getContinous_pickup() + ","
				+ stoptimes.getContinous_dropoff() + "," + stoptimes.getShape_dist_traveled() + ","
				+ stoptimes.getTimepoint();

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getStop_Times());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		Stop_TimesValues stoptimesvalues = new Stop_TimesValues();
		if(GTFSCheckStopTimes.checkStopTimesMandatoryFields(stopTimesValues) && GTFSCheckStopTimes.checkarrivaltime(stopTimesValues) && GTFSCheckStopTimes.checkdeparturetime(stopTimesValues)) {
		for (int i = 0; i < stopTimesValues.size(); i++) {
			stoptimesvalues.setTrip_id(stopTimesValues.get(i).getTrip_id());
			stoptimesvalues.setArrival_time(stopTimesValues.get(i).getArrival_time());
			stoptimesvalues.setDeparture_time(stopTimesValues.get(i).getDeparture_time());
			stoptimesvalues.setStop_id(stopTimesValues.get(i).getStop_id());
			stoptimesvalues.setStop_sequence(stopTimesValues.get(i).getStop_sequence());
			stoptimesvalues.setStop_headsign(stopTimesValues.get(i).getStop_headsign());
			stoptimesvalues.setPickyp_type(stopTimesValues.get(i).getPickyp_type());
			stoptimesvalues.setDropoff_type(stopTimesValues.get(i).getDropoff_type());

			stoptimesvalues.setContinous_pickyp(stopTimesValues.get(i).getContinous_pickyp());
			stoptimesvalues.setContinous_dropoff(stopTimesValues.get(i).getContinous_dropoff());
			stoptimesvalues.setShape_dist_traveled(stopTimesValues.get(i).getShape_dist_traveled());
			stoptimesvalues.setTimepoint(stopTimesValues.get(i).getTimepoint());
			writer.write(stoptimesvalues.getTrip_id() + ",");
			writer.write(stoptimesvalues.getArrival_time() + ",");
			writer.write(stoptimesvalues.getDeparture_time() + ",");
			writer.write(stoptimesvalues.getStop_id().toString() + ",");
			writer.write(stoptimesvalues.getStop_headsign() + ",");
			writer.write(stoptimesvalues.getPickyp_type() + ",");
			writer.write(stoptimesvalues.getDropoff_type() + ",");
			writer.write(stoptimesvalues.getContinous_pickyp() + ",");
			writer.write(stoptimesvalues.getShape_dist_traveled() + ",");
			writer.write(stoptimesvalues.getTimepoint() + ",");
			writer.write(System.getProperty("line.separator"));

		}
		writer.close();
		}
	}

	private static void writeStop_Times() {
		// TODO Auto-generated method stub

	}

	public static void main(String[] args) throws IOException {
		writeStop_Times();
	}

}
