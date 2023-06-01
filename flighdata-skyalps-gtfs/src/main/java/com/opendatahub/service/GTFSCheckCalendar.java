// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.service;

import java.io.IOException;
import java.util.ArrayList;

import com.opendatahub.validation.CheckLocationType;
import com.opendatahub.dto.CalendarValues;

public class GTFSCheckCalendar extends Exception{
	

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;


	public GTFSCheckCalendar(String errorMessage) {
		super(errorMessage);
	}


	public static boolean checkcalendarValues(ArrayList<CalendarValues> calendarvalues) throws GTFSCheckCalendar  {
		for(int i = 0; i < calendarvalues.size(); i++) {
		if(calendarvalues.get(i).getService_id() != null && calendarvalues.get(i).getEnd_date() != null && String.valueOf(calendarvalues.get(i).getMonday()) != null && String.valueOf(calendarvalues.get(i).getTuesday()) != null && String.valueOf(calendarvalues.get(i).getWednesday()) != null && String.valueOf(calendarvalues.get(i).getThursday()) != null && String.valueOf(calendarvalues.get(i).getFriday()) != null && String.valueOf(calendarvalues.get(i).getSaturday()) != null && calendarvalues.get(i).getStart_date() != null) {
			if(!calendarvalues.get(i).getService_id().toString().isBlank() && !calendarvalues.get(i).getEnd_date().toString().isBlank() && !String.valueOf(calendarvalues.get(i).getMonday()).isBlank() && !String.valueOf(calendarvalues.get(i).getTuesday()).isBlank() && !String.valueOf(calendarvalues.get(i).getWednesday()).isBlank() && !String.valueOf(calendarvalues.get(i).getThursday()).isBlank() && !String.valueOf(calendarvalues.get(i).getFriday()).isBlank() && !String.valueOf(calendarvalues.get(i).getSaturday()).isBlank() && !String.valueOf(calendarvalues.get(i).getSunday()).isBlank() && !calendarvalues.get(i).getStart_date().isBlank()) {
				return true;
			}
		} else {
			throw new GTFSCheckCalendar("Error: Fields are mandatory"); 
		}
			
		
		}
		throw new GTFSCheckCalendar("Error: Fields are mandatory"); 
	
	}

	private static void checkcalendarValues() {
		// TODO Auto-generated method stub

	} 
	
	
	@CheckLocationType
	public static void main(String[] args) throws IOException {
		checkcalendarValues();
	}

}