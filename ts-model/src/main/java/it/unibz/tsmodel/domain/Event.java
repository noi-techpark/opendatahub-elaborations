package it.unibz.tsmodel.domain;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;

import org.hibernate.annotations.GenericGenerator;

import com.thoughtworks.xstream.annotations.XStreamAlias;

/**
 * @author mreinstadler this class represents one specific 
 * event with description and id
 *
 */
@XStreamAlias("event")
@Entity
public class Event implements ObservationMetaInfo{
	
	
	private String description = "no event registered";
	@Id
	@GenericGenerator(name = "generator", strategy = "increment", parameters = {})
	@GeneratedValue(generator = "generator")
	private int id= -1;
	
	/**
	 * @param descr the description of the event
	 * @param id the id of the event
	 */
	public Event(String descr, int id){
		this.description = descr;
		this.id = id;
	}
	
	/**
	 * Empty constructor for the Event object
	 */
	public Event(){
		
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
		sb.append("event identifier: "+ this.id+ nl);
		sb.append("event description: "+ this.description+ nl);
		return sb.toString();
	}

	
	
}
