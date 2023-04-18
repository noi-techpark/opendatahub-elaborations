package com.opendatahub.service;

import java.io.IOException;
import java.util.ArrayList;

import com.opendatahub.Validation.CheckLocationType;
import com.opendatahub.dto.AgencyValues;
import com.opendatahub.dto.StopsValue;

public class GTFSCheckAgency extends Exception{
	

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;


	public GTFSCheckAgency(String errorMessage) {
		super(errorMessage);
	}


	public static boolean checkAgencyMandatoryFields(ArrayList<AgencyValues>  agencyvalues) throws GTFSCheckAgency  {
		for(int i = 0; i < agencyvalues.size(); i++) {
			if(agencyvalues.get(i).getAgency_timezone() != null && agencyvalues.get(i).getAgency_name() != null && agencyvalues.get(i).getAgency_url() != null) {
					if(!agencyvalues.get(i).getAgency_timezone().toString().isBlank() && !agencyvalues.get(i).getAgency_name().isBlank() && !agencyvalues.get(i).getAgency_url().toString().isBlank()) {
					return true;
					} else {
						throw new GTFSCheckAgency("Error: Agency ID, Agency Name, Agency URL are mandatory");
					}
				
					
			} 
			
		
		}
		throw new GTFSCheckAgency("Error: Agency ID, Agency Name, Agency URL are mandatory"); 
	
	}

	private static void checkAgencyMandatoryFields() {
		// TODO Auto-generated method stub

	} 
	
	
	@CheckLocationType
	public static void main(String[] args) throws IOException {
		checkAgencyMandatoryFields();
	}

}
