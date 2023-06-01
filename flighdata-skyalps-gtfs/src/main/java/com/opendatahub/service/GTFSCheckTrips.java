// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.service;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Scanner;

import org.apache.tomcat.util.http.fileupload.FileUtils;

import com.opendatahub.validation.CheckLocationType;
import com.opendatahub.dto.AgencyValues;
import com.opendatahub.dto.TripsValues;

public class GTFSCheckTrips extends Exception{
	

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;


	public GTFSCheckTrips(String errorMessage) {
		super(errorMessage);
	}


	public static boolean checkTripsMandatoryFields(ArrayList<TripsValues>  tripsvalues) throws GTFSCheckTrips  {
		for(int i = 0; i < tripsvalues.size(); i++) {
			if(tripsvalues.get(i).getRoute_id() != null && tripsvalues.get(i).getService_id() != null && tripsvalues.get(i).getTrip_id() != null) {
					if(!tripsvalues.get(i).getRoute_id().toString().isBlank() && !tripsvalues.get(i).getService_id().isBlank() && !tripsvalues.get(i).getTrip_id().toString().isBlank()) {
					return true;
					} else {
						throw new GTFSCheckTrips("Error: Route ID, Service ID, Trip ID are mandatory");
					}
				
					
			} 
			
		
		}
		throw new GTFSCheckTrips("Error: Route ID, Service ID, Trip ID are mandatory"); 
	
	}

	private static void checkTripsMandatoryFields() {
		// TODO Auto-generated method stub

	} 

	
	
	@CheckLocationType
	public static void main(String[] args) throws IOException {
		checkTripsMandatoryFields();
	}

}
