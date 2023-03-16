package it.noitechpark.service;

import java.io.IOException;
import java.util.ArrayList;

import it.noiteachpark.Validation.CheckLocationType;
import it.noitechpark.dto.AgencyValues;
import it.noitechpark.dto.Stop_TimesValues;

public class GTFSCheckStopTimes  extends Exception{
	

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;


	public GTFSCheckStopTimes(String errorMessage) {
		super(errorMessage);
	}


	public static boolean checkStopTimesMandatoryFields(ArrayList<Stop_TimesValues>  stoptimesvalues) throws GTFSCheckStopTimes  {
		for(int i = 0; i < stoptimesvalues.size(); i++) {
			if(stoptimesvalues.get(i).getTrip_id() != null && stoptimesvalues.get(i).getStop_id() != null && stoptimesvalues.get(i).getStop_sequence() != null) {
					if(!stoptimesvalues.get(i).getTrip_id().toString().isBlank() && !stoptimesvalues.get(i).getStop_id().isBlank() && !stoptimesvalues.get(i).getStop_sequence().toString().isBlank()) {
					return true;
					} else {
						throw new GTFSCheckStopTimes("Error: Trip ID, Stop ID, Stop Sequence are mandatory");
					}
				
					
			} 
			
		
		}
		throw new GTFSCheckStopTimes("Error: Trip ID, Stop ID, Stop Sequence are mandatory"); 
	
	}

	private static void checkStopTimesMandatoryFields() {
		// TODO Auto-generated method stub

	} 
	
	public static boolean checkarrivaltime(ArrayList<Stop_TimesValues>  stoptimesvalues) throws GTFSCheckStopTimes  {
		for(int i = 0; i < stoptimesvalues.size(); i++) {
			if(stoptimesvalues.get(i).getTimepoint() != null) {
					if(!stoptimesvalues.get(i).getTimepoint().toString().isBlank()) {
						if(stoptimesvalues.get(i).getTimepoint().getValue() == 1 ||  stoptimesvalues.get(i).getTimepoint().getValue() == 0) {
						if(stoptimesvalues.get(i).getArrival_time() != null) {
							if(!stoptimesvalues.get(i).getArrival_time().isBlank()) {
					return true; 
							} else { throw new GTFSCheckStopTimes("Error: Stop Sequence error");}
						} else { throw new GTFSCheckStopTimes("Error: Stop Sequence error");}
						} else {
							throw new GTFSCheckStopTimes("Error: Stop Sequence error");
						}
					} else {
						throw new GTFSCheckStopTimes("Error: Stop Sequence error");
					}
				
					
			} 
			
		
		}
		throw new GTFSCheckStopTimes("Error: Stop Sequence error"); 
	
	}

	private static void checkarrivaltime() {
		// TODO Auto-generated method stub

	} 
	
	public static boolean checkdeparturetime(ArrayList<Stop_TimesValues>  stoptimesvalues) throws GTFSCheckStopTimes  {
		for(int i = 0; i < stoptimesvalues.size(); i++) {
			if(stoptimesvalues.get(i).getTimepoint() != null) {
					if(!stoptimesvalues.get(i).getTimepoint().toString().isBlank()) {
						if(stoptimesvalues.get(i).getTimepoint().getValue() == 1 ||  stoptimesvalues.get(i).getTimepoint().getValue() == 0) {
						if(stoptimesvalues.get(i).getArrival_time() != null) {
							if(!stoptimesvalues.get(i).getArrival_time().isBlank()) {
					return true; 
							} else { throw new GTFSCheckStopTimes("Error: Stop Sequence error");}
						} else { throw new GTFSCheckStopTimes("Error: Stop Sequence error");}
						} else {
							throw new GTFSCheckStopTimes("Error: Stop Sequence error");
						}
					} else {
						throw new GTFSCheckStopTimes("Error: Stop Sequence error");
					}
				
					
			} 
			
		
		}
		throw new GTFSCheckStopTimes("Error: Stop Sequence error"); 
	
	}

	private static void checkdeparturetime() {
		// TODO Auto-generated method stub

	} 
	
	@CheckLocationType
	public static void main(String[] args) throws IOException {
		checkdeparturetime();
		checkarrivaltime();
		checkStopTimesMandatoryFields();
	}

}
