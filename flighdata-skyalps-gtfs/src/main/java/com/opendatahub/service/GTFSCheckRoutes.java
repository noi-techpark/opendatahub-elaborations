package com.opendatahub.service;

import java.io.IOException;
import java.util.ArrayList;
import com.opendatahub.validation.CheckLocationType;
import com.opendatahub.dto.RoutesValues;

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
