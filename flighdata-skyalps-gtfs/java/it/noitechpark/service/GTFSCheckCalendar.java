package it.noitechpark.service;

import java.io.IOException;
import java.util.ArrayList;

import it.noiteachpark.Validation.CheckLocationType;
import it.noitechpark.dto.CalendarValues;
import it.noitechpark.dto.Calendar_DatesValues;

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
		if(calendarvalues.get(i).getService_id() != null && calendarvalues.get(i).getEnd_date() != null && calendarvalues.get(i).getMonday() != null && calendarvalues.get(i).getTuesday() != null && calendarvalues.get(i).getWednesday() != null && calendarvalues.get(i).getThursday() != null && calendarvalues.get(i).getFriday() != null && calendarvalues.get(i).getSaturday() != null && calendarvalues.get(i).getStart_date() != null) {
			if(!calendarvalues.get(i).getService_id().toString().isBlank() && !calendarvalues.get(i).getEnd_date().toString().isBlank() && !calendarvalues.get(i).getMonday().toString().isBlank() && !calendarvalues.get(i).getTuesday().toString().isBlank() && !calendarvalues.get(i).getWednesday().toString().isBlank() && !calendarvalues.get(i).getThursday().toString().isBlank() && !calendarvalues.get(i).getFriday().toString().isBlank() && !calendarvalues.get(i).getSaturday().toString().isBlank() && !calendarvalues.get(i).getStart_date().isBlank()) {
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