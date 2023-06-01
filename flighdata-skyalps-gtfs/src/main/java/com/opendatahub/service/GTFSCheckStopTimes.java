// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.service;

import java.io.IOException;
import java.util.ArrayList;

import com.opendatahub.validation.CheckLocationType;
import com.opendatahub.dto.AgencyValues;
import com.opendatahub.dto.Stop_TimesValues;

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
			if(stoptimesvalues.get(i).getTrip_id() != null && stoptimesvalues.get(i).getStop_id() != null) {
					if(!stoptimesvalues.get(i).getTrip_id().toString().isBlank() && !stoptimesvalues.get(i).getStop_id().isBlank()) {
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
	
	
	@CheckLocationType
	public static void main(String[] args) throws IOException {
		checkStopTimesMandatoryFields();
	}

}
