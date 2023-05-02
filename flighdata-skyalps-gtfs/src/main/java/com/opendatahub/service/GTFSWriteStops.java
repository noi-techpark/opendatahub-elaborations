package com.opendatahub.service;


import java.io.FileWriter;



import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.opendatahub.validation.CheckLocationType;
import com.opendatahub.constantsClasses.Stops;
import com.opendatahub.dto.AgencyValues;
import com.opendatahub.dto.StopsValue;
import com.opendatahub.enumClasses.location_type;
public class GTFSWriteStops {

	
	public static void writeStops(ArrayList<StopsValue>  stopsvalues) throws IOException, MalformedURLException, GTFSCheckStops { 
	
		Stops stopsValue = new Stops();
		
		StopsValue stopsValues2 = new StopsValue();
		
			
		
		String firstLine = stopsValue.getStopdi() + "," + stopsValue.getStopcode() + "," + stopsValue.getStopname()
				+ "," + stopsValue.getStop_lat() + "," + stopsValue.getStop_lon();

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getStops());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		if(GTFSCheckStops.checkStopNameStopLatStopLon(stopsvalues) && GTFSCheckStops.checkstopid(stopsvalues)) {
			System.out.println("Before removing duplicates : " + Arrays.toString(stopsvalues.toArray()));

			final List<StopsValue> listWithoutDuplicates = new ArrayList<>(
			new HashSet<>(stopsvalues));

			Set<StopsValue> uniqueStops = new HashSet<>(stopsvalues);

			System.out.println("After removing duplicates :: "
			                     + Arrays.toString(stopsvalues.toArray()));
			for (StopsValue stop : uniqueStops) {
				if (stop.getStop_lat() != null && stop.getStop_lon() != null) {
			/*stopsValues2.setStop_id(stop.get(i).getStop_id());
			stopsValues2.setStop_code(stop.get(i).getStop_code());
			
			stopsValues2.setStop_name( stop.get(i).getStop_name());
			stopsValues2.setStop_lat(stop.get(i).getStop_lat());
			stopsValues2.setStop_lon(stop.get(i).getStop_lon());*/
			
			writer.write(stop.getStop_id() + ",");
			writer.write(stop.getStop_code() + ",");
			writer.write(stop.getStop_name().toString() + ",");
			writer.write(String.valueOf(stop.getStop_lat()) + ",");
			writer.write(String.valueOf(stop.getStop_lon()));
			writer.write(System.getProperty("line.separator"));
				}
		}
		writer.close();
	}
	}

	private static void writeStops() {
		// TODO Auto-generated method stub

	}
	@CheckLocationType
	public static void main(String[] args) throws IOException {
		 writeStops();
	}

}
