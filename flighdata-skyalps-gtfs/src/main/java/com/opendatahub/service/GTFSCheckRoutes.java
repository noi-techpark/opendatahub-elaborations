package com.opendatahub.service;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.stream.Stream;

import com.opendatahub.validation.CheckLocationType;
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
			if(routesvalues.get(i).getRoute_id() != null && routesvalues.get(i).getRoute_type() != null) {
					if(!routesvalues.get(i).getRoute_id().isBlank() && !routesvalues.get(i).getRoute_type().toString().isBlank()) {
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
	
	public static boolean checkagencyid(ArrayList<RoutesValues>  routesvalues) throws GTFSCheckRoutes, IOException  {
		if(GTFSReadFileFolder.getAgency().length() != 0) {
			long count = 0; 
			try (Stream<String> stream = Files.lines(GTFSReadFileFolder.getAgency().toPath(), StandardCharsets.UTF_8)) {
				count = stream.count();
				}
			if(count > 1) {
				for(int i = 0; i < routesvalues.size(); i++) {
					if(routesvalues.get(i).getAgency_id() != null) {
						if(!routesvalues.get(i).getAgency_id().isBlank()) {
							return true;
						} else {
							throw new GTFSCheckRoutes("Error: Routes Agency ID is mandatory");
						}
					} else {
						throw new GTFSCheckRoutes("Error: Routes Agency ID is mandatory");
					}
				}
			} else {
				return true;
			}
		} else if (GTFSReadFileFolder.getAgency().length() != 0) {
		return true;
	
	}
		return false;
	}

	private static void checkagencyid() {
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
	
	private static boolean checkroutelongname(ArrayList<RoutesValues> routesvalues) throws GTFSCheckRoutes {
		for(int i = 0; i < routesvalues.size(); i++) {
			if(routesvalues.get(i).getRoute_long_name() != null) {
				if(!routesvalues.get(i).getRoute_long_name().isBlank()) {
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
	
	public static boolean checkrouteshortandlongname(ArrayList<RoutesValues>  routesvalues) throws GTFSCheckRoutes, IOException  {
			if(checkrouteshortname(routesvalues) == true || checkroutelongname(routesvalues) == true) {
				return true;
			} else {
				return false;
			}
	}

	private static void checkrouteshortandlongname() {
		// TODO Auto-generated method stub

	}
	
	
	@CheckLocationType
	public static void main(String[] args) throws IOException {
		checkrouteshortandlongname();
		checkagencyid();
		checkRoutesMandatoryFields();
	}

}
