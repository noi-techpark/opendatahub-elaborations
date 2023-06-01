// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsforecast.domain;

import java.sql.Timestamp;
import java.util.ArrayList;

import flexjson.JSONSerializer;


public class ParkingForecasts {
	private Timestamp timestamp= null;
	private ArrayList<ParkingForecast> parkingForecasts = null;
	
	
	public ParkingForecasts(){
		this.parkingForecasts = new ArrayList<ParkingForecast>();
	}
	/**
	 * @return the timestamp
	 */
	public Timestamp getTimestamp() {
		return timestamp;
	}
	/**
	 * @param timestamp the timestamp to set
	 */
	public void setTimestamp(Timestamp timestamp) {
		this.timestamp = timestamp;
	}
	/**
	 * @return the parkingForecasts
	 */
	public ArrayList<ParkingForecast> getParkingForecasts() {
		return parkingForecasts;
	}
	/**
	 * @param parkingForecasts the parkingForecasts to set
	 */
	public void setParkingForecasts(ArrayList<ParkingForecast> parkingForecasts) {
		this.parkingForecasts = parkingForecasts;
	}
	public void addOneParkingforecast(ParkingForecast f){
		this.parkingForecasts.add(f);
	}

	/**
	 * @return a string in JSON format. It includes the list of {@link ParkingForecast}, which 
	 * is essential for the final result
	 */
	public String parkingForecastsToJSON(){
		return new JSONSerializer().exclude("*.class").include("parkingForecasts").serialize(this);
	}
	
	
	
}
