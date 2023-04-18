package com.opendatahub.service;


import java.io.FileWriter;



import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.List;

import com.opendatahub.Validation.CheckLocationType;
import com.opendatahub.constantsClasses.Stops;
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
		for (int i = 0; i < stopsvalues.size(); i++) {
			stopsValues2.setStop_id(stopsvalues.get(i).getStop_id());
			stopsValues2.setStop_code(stopsvalues.get(i).getStop_code());
			
			stopsValues2.setStop_name( stopsvalues.get(i).getStop_name());
			stopsValues2.setStop_lat(stopsvalues.get(i).getStop_lat());
			stopsValues2.setStop_lon(stopsvalues.get(i).getStop_lon());
	        
			writer.write(stopsValues2.getStop_id() + ",");
			writer.write(stopsValues2.getStop_code() + ",");
			writer.write(stopsValues2.getStop_name().toString() + ",");
			writer.write(stopsValues2.getStop_lat() + ",");
			writer.write(stopsValues2.getStop_lon() + ",");
			writer.write(System.getProperty("line.separator"));

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
