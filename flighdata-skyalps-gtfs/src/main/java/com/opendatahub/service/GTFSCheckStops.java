// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

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
		throw new GTFSCheckStops("Error: Stop name or Stop lon or Stop lat must not be null"); 
	
	}

	private static void checkStopNameStopLatStopLon() {
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

	
	@CheckLocationType
	public static void main(String[] args) throws IOException {
		checkstopid();
		checkStopNameStopLatStopLon();
	}

}
