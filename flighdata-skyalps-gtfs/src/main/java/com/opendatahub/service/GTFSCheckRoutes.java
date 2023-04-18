package com.opendatahub.service;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.stream.Stream;

import com.opendatahub.Validation.CheckLocationType;
import com.opendatahub.dto.AgencyValues;
import com.opendatahub.dto.RoutesValues;
import com.opendatahub.dto.StopsValue;

public class GTFSCheckRoutes  extends Exception{
	

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;


	public GTFSCheckRoutes(String errorMessage) {
		super(errorMessage);
	}


	public static boolean checkRoutesMandatoryFields(ArrayList<RoutesValues>  routesvalues) throws GTFSCheckRoutes  {
		for(int i = 0; i < routesvalues.size(); i++) {
			if(routesvalues.get(i).getRoute_id() != null) {
					if(!routesvalues.get(i).getRoute_id().isBlank()) {
					return true;
					} else {
						throw new GTFSCheckRoutes("Error: Route ID and Route Type are mandatory");
					}
				
					
			} 
			
		
		}
		throw new GTFSCheckRoutes("Error: Routes ID and Route Type are mandatory"); 
	
	}

	private static void checkRoutesMandatoryFields() {
		// TODO Auto-generated method stub

	} 
	
	private static boolean checkrouteshortname(ArrayList<RoutesValues> routesvalues) throws GTFSCheckRoutes {
		for(int i = 0; i < routesvalues.size(); i++) {
			if(routesvalues.get(i).getRoute_short_name() != null) {
				if(!routesvalues.get(i).getRoute_short_name().isBlank()) {
					return true;
				} else {
					return false;
				}
		} else {
			return false;
		}
	}
		return false;
	}
	
	
	
	@CheckLocationType
	public static void main(String[] args) throws IOException {
		checkRoutesMandatoryFields();
	}

}
