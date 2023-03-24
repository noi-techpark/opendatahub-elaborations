package com.opendatahub.service;

import java.io.IOException;
import java.util.ArrayList;

import com.opendatahub.validation.CheckLocationType;
import com.opendatahub.dto.Calendar_DatesValues;
import com.opendatahub.dto.TripsValues;

public class GTFSCheckCalendarDates  extends Exception{
	

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;


	public GTFSCheckCalendarDates(String errorMessage) {
		super(errorMessage);
	}


	public static boolean checkCalendarDatesMandatoryFields(ArrayList<Calendar_DatesValues>  calendardatevalues) throws GTFSCheckCalendarDates  {
		for(int i = 0; i < calendardatevalues.size(); i++) {
			if(calendardatevalues.get(i).getService_id() != null && calendardatevalues.get(i).getDate() != null && calendardatevalues.get(i).getException_type() != null) {
					if(!calendardatevalues.get(i).getService_id().toString().isBlank() && !calendardatevalues.get(i).getException_type().toString().isBlank() && !calendardatevalues.get(i).getDate().toString().isBlank()) {
					return true;
					} else {
						throw new GTFSCheckCalendarDates("Error: Service ID, Date, Exception_type are mandatory");
					}
				
					
			} 
			
		
		}
		throw new GTFSCheckCalendarDates("Error: Service ID, Date, Exception_type are mandatory"); 
	
	}

	private static void checkCalendarDatesMandatoryFields() {
		// TODO Auto-generated method stub

	} 
	
	
	@CheckLocationType
	public static void main(String[] args) throws IOException {
		checkCalendarDatesMandatoryFields();
	}

}
