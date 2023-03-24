package com.opendatahub.service;


import java.io.FileWriter;



import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.List;

import com.opendatahub.validation.CheckLocationType;
import com.opendatahub.constantsClasses.Stops;
import com.opendatahub.dto.StopsValue;
import com.opendatahub.enumClasses.location_type;
public class GTFSWriteStops {

	
	public static void writeStops(ArrayList<StopsValue>  stopsvalues) throws IOException, MalformedURLException, GTFSCheckStops { 
	
		Stops stopsValue = new Stops();
		
		StopsValue stopsValues2 = new StopsValue();
	
		for(int i = 0; i < stopsvalues.size(); i++) {
			if(stopsvalues.get(i).getLocation_type().getValue() == 1 || stopsvalues.get(i).getLocation_type().getValue() == 0 || stopsvalues.get(i).getLocation_type().getValue() == 2) {
				
				stopsvalues.get(i).getStop_name();
			}
		}
		
		
		
		
		String firstLine = stopsValue.getStopdi() + "," + stopsValue.getStopcode() + "," + stopsValue.getStopname()
				+ "," + stopsValue.getTt_stop_name() + "," + stopsValue.getStop_desc() + "," + stopsValue.getStop_lat()
				+ "," + stopsValue.getStop_lon() + "," + stopsValue.getZone_id() + "," + stopsValue.getStop_URL() + ","
				+ stopsValue.getLocation_type() + "," + stopsValue.getParent_station() + ","
				+ stopsValue.getStop_timezone() + "," + stopsValue.getWheelchair_boarding() + ","
				+ stopsValue.getLevel_id() + "," + stopsValue.getPlatform_code();

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getStops());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		if(GTFSCheckStops.checkStopNameStopLatStopLon(stopsvalues) && GTFSCheckStops.checkzoneid(stopsvalues) && GTFSCheckStops.checkstopid(stopsvalues) && GTFSCheckStops.checkparentstation(stopsvalues)) {
		for (int i = 0; i < stopsvalues.size(); i++) {
			stopsValues2.setStop_id(stopsvalues.get(i).getStop_id());
			stopsValues2.setStop_code(stopsvalues.get(i).getStop_code());
			
			stopsValues2.setStop_name( stopsvalues.get(i).getStop_name());
			stopsValues2.setTts_stop_name(stopsvalues.get(i).getTts_stop_name());
			stopsValues2.setStop_desc(stopsvalues.get(i).getStop_desc());
			stopsValues2.setStop_lat(stopsvalues.get(i).getStop_lat());
			stopsValues2.setStop_lon(stopsvalues.get(i).getStop_lon());
			stopsValues2.setZone_id(stopsvalues.get(i).getZone_id());

			stopsValues2.setStop_URL(stopsvalues.get(i).getStop_URL());
			;
			stopsValues2.setLocation_type(stopsvalues.get(i).getLocation_type());
			stopsValues2.setParent_station(stopsvalues.get(i).getParent_station());
			stopsValues2.setStop_timezone(stopsvalues.get(i).getStop_timezone());
			stopsValues2.setWheelchair_boarding(stopsvalues.get(i).getWheelchair_boarding());
			stopsValues2.setLevel_id(stopsvalues.get(i).getLevel_id());
			stopsValues2.setPlatform_code(stopsvalues.get(i).getPlatform_code());
	        
			writer.write(stopsValues2.getStop_id() + ",");
			writer.write(stopsValues2.getStop_code() + ",");
			writer.write(stopsValues2.getStop_name().toString() + ",");
			writer.write(stopsValues2.getTts_stop_name() + ",");
			writer.write(stopsValues2.getStop_desc() + ",");
			writer.write(stopsValues2.getStop_lat() + ",");
			writer.write(stopsValues2.getStop_lon() + ",");
			writer.write(stopsValues2.getZone_id() + ",");

			writer.write(stopsValues2.getStop_URL() + ",");
			writer.write(stopsValues2.getLocation_type() + ",");
			writer.write(stopsValues2.getParent_station() + ",");
			writer.write(stopsValues2.getStop_timezone() + ",");
			writer.write(stopsValues2.getStop_desc() + ",");
			writer.write(stopsValues2.getWheelchair_boarding() + ",");
			writer.write(stopsValues2.getLevel_id() + ",");
			writer.write(stopsValues2.getPlatform_code().toString());
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
