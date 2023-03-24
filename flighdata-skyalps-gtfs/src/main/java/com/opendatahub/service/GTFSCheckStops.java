package com.opendatahub.service;

import java.io.FileWriter;
import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;

import com.opendatahub.validation.CheckLocationType;
import com.opendatahub.constantsClasses.Stops;
import com.opendatahub.dto.StopsValue;

public class GTFSCheckStops extends Exception {
	
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	public GTFSCheckStops(String errorMessage) {
		super(errorMessage);
	}


	public static boolean checkStopNameStopLatStopLon(ArrayList<StopsValue>  stopsvalues) throws GTFSCheckStops  {
		for(int i = 0; i < stopsvalues.size(); i++) {
			if(stopsvalues.get(i).getLocation_type().getValue() != 0 || stopsvalues.get(i).getLocation_type().getValue() != 1 || stopsvalues.get(i).getLocation_type().getValue() != 2) {
	
				if(stopsvalues.get(i).getStop_name() != null || stopsvalues.get(i).getStop_lon() != null || stopsvalues.get(i).getStop_lat() != null) {
					if(!stopsvalues.get(i).getStop_name().isBlank()) {
					return true;
					} else {
						throw new GTFSCheckStops("Error: Stop name must not be blank");
					}
				} else {
					throw new GTFSCheckStops("Error: Stop name or Stop lon or Stop lat must not be null");
				} 
					
			} 
			
		
		}
		throw new GTFSCheckStops("Error: Stop name or Stop lon or Stop lat must not be null"); 
	
	}

	private static void checkStopNameStopLatStopLon() {
		// TODO Auto-generated method stub

	} 
	
	public static boolean checkzoneid(ArrayList<StopsValue>  stopsvalues) throws GTFSCheckStops  {
		if(GTFSReadFileFolder.getFare_rules().length() != 0) {
		for(int i = 0; i < stopsvalues.size(); i++) {
				if(stopsvalues.get(i).getZone_id() != null) {
					if(!stopsvalues.get(i).getZone_id().isBlank()) {
					return true;
					} else {
						throw new GTFSCheckStops("Error: Zone id is required");
					}
				} else {
					throw new GTFSCheckStops("Error: Zone id is required");
				} 
					
			} 
			
		
		} else if (GTFSReadFileFolder.getFare_rules().length() == 0) {
		return true;
	
	}
		return false;
	}

	private static void checkzoneid() {
		// TODO Auto-generated method stub

	}
	
	public static boolean checkstopid(ArrayList<StopsValue>  stopsvalues) throws GTFSCheckStops  {
		for(int i = 0; i < stopsvalues.size(); i++) {
				if(stopsvalues.get(i).getStop_id() != null) {
					if(!stopsvalues.get(i).getStop_id().isBlank()) {
					return true;
					} else {
						throw new GTFSCheckStops("Error: Stopid id is required");
					}
				} else {
					throw new GTFSCheckStops("Error: Stopid id is required");
				} 
					
			} 
			
		
		
		return false;
	}

	private static void checkstopid() {
		// TODO Auto-generated method stub

	} 
	
	public static boolean checkparentstation(ArrayList<StopsValue>  stopsvalues) throws GTFSCheckStops  {
		for(int i = 0; i < stopsvalues.size(); i++) {
			if(stopsvalues.get(i).getLocation_type() != null) {
				if(stopsvalues.get(i).getParent_station() != null) {
					return true;
				} else {
					throw new GTFSCheckStops("Error: Parent station is required");
				} 
			}
			} 
			
		
		
		return false;
	}

	private static void checkparentstation() {
		// TODO Auto-generated method stub

	}
	
	@CheckLocationType
	public static void main(String[] args) throws IOException {
		checkparentstation();
		checkstopid();
		checkzoneid();
		checkStopNameStopLatStopLon();
	}

}
