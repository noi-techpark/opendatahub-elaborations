// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsforecast.entity;

import com.thoughtworks.xstream.annotations.XStreamAlias;

/**
 * @author mreinstadler this class represents one specific 
 * event with the meta information (the description, the position, ect)
 *
 */
@XStreamAlias("event")
public class Event implements ObservationMetaInfo{
	
	private String description = "no event registered";
	
	/**
	 * @param id the id to set
	 */
	public void setId(int id) {
		this.id = id;
	}

	private int id= -1;
	
	/**
	 * @param descr the description of the event
	 * @param id the id of the event
	 */
	public Event(String descr, int id){
		this.description = descr;
		this.id = id;
	}
	
	public Event(){
		this.description = "";
		this.id = -1;
	}
	/**
	 * @return the description
	 */
	public String getDescription() {
		return description;
	}

	/**
	 * @param description the description to set
	 */
	public void setDescription(String description) {
		this.description = description;
	}

	/**
	 * @return the id
	 */
	public int getId() {
		return id;
	}

	
	
	
}
