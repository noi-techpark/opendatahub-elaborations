// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.domain;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;

import org.hibernate.annotations.GenericGenerator;

import com.thoughtworks.xstream.annotations.XStreamAlias;

/**
 * @author mreinstadler
 * this class represents one holiday with the description 
 * and possible other meta informations
 *
 */
@XStreamAlias("holiday")
@Entity
public class Holiday implements ObservationMetaInfo {
	private String description = "no holiday registered";
	@Id
	@GenericGenerator(name = "generator", strategy = "increment", parameters = {})
	@GeneratedValue(generator = "generator")
	private int id= -1;
   
	
	/**
	 * @param descr the textual description of the holiday
	 * @param id the id of the holiday
	 */
	public Holiday(String descr, int id){
		this.description = descr;
		this.id = id;
	}
	/**
	 * empty constructor
	 */
	public Holiday(){
		
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
	/**
	 * @param id the id to set
	 */
	public void setId(int id) {
		this.id = id;
	}
	
	@Override
	public String toString(){
		StringBuilder sb= new StringBuilder();
		String nl = System.getProperty("line.separator");
		sb.append("holiday identifier: "+ this.id+ nl);
		sb.append("holiday description: "+ this.description+ nl);
		return sb.toString();
	}
	
	
}
