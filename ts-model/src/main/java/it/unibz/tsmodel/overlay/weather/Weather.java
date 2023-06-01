// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.overlay.weather;

import it.unibz.tsmodel.domain.ObservationMetaInfo;

import com.thoughtworks.xstream.annotations.XStreamAlias;

/**
 * @author mreinstadler
 * this class represents one weather object with the
 * meta information. The information are not from the 
 * database, but from OpenWeatherMap
 *
 */
@XStreamAlias("weather")
public class Weather implements ObservationMetaInfo{
	private String description = "no data available";
	private int id= -1;
	private int mintemp=-1;
	private int maxtemp = -1;
	
	
	/**
	 * @param id the code of the weather
	 * @param description the description
	 * @param min the min temperature in Kelvin
	 * @param max the max temperature in Kelvin
	 */
	public Weather(int id, String description, int min, int max){
		this.description = description;
		this.id = id;
		this.mintemp = min;
		this.maxtemp = max;
	}
	
	public Weather(){
		
	}
	/**
	 * @return the description of the weather
	 */
	public String getDescription() {
		return description;
	}
	/**
	 * @param description the description of the weather
	 */
	public void setDescription(String description) {
		this.description = description;
	}
	/**
	 * @return the code of the weather
	 */
	public int getId() {
		return id;
	}
	/**
	 * @param id the code of the weather
	 */
	public void setId(int id) {
		this.id = id;
	}
	/**
	 * @return the minimum temperature in Kelvin
	 */
	public int getMintemp() {
		return mintemp;
	}
	/**
	 * @param mintemp the minimum temperature in Kelvin
	 */
	public void setMintemp(int mintemp) {
		this.mintemp = mintemp;
	}
	/**
	 * @return the maximum temperature in Kelvin
	 */
	public int getMaxtemp() {
		return maxtemp;
	}
	/**
	 * @param maxtemp the maximum temperature in Kelvin
	 */
	public void setMaxtemp(int maxtemp) {
		this.maxtemp = maxtemp;
	}
	
	@Override
	public String toString(){
		StringBuilder sb= new StringBuilder();
		String nl = System.getProperty("line.separator");
		sb.append("weather description: "+ this.description+ nl);
		sb.append("min temperature: "+ this.mintemp+ nl);
		sb.append("max temperature: "+ this.maxtemp+ nl);
		return sb.toString();
	}
	

}
