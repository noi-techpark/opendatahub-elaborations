package it.unibz.tsforecast.entity;
import com.thoughtworks.xstream.annotations.XStreamAlias;

/**
 * @author mreinstadler
 * this class represents one holiday with the description 
 * and possible other meta informations
 *
 */
@XStreamAlias("holiday")
public class Holiday implements ObservationMetaInfo {
	private String description = "no holiday registered";
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
	
	
	
	
}
