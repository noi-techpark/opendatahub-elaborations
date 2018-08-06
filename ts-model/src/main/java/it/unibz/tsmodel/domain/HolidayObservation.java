package it.unibz.tsmodel.domain;
import java.sql.Timestamp;
import java.util.Calendar;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;

import org.apache.commons.lang3.time.DateUtils;
/**
 * @author mreinstadler
 * This class represents one holiday observation stored in 
 * the DB. The timestamp is the primary key and the observed
 * the foreign key to the holiday record. The timestamp is daily
 * with hours, minutes, seconds and milliseconds zero
 *
 */
@Entity
public class HolidayObservation implements Observation {
	
	@Column(name = "holiday_id")
	private int observedValue = -1;
	@Id
	private Timestamp timestamp;

	
	public HolidayObservation(){
		
	}
	/**
	 * This creates a new object by truncating the timestamp with 
	 * hour=0, minute=0, seconds=0 and milliseconds = 0
	 * @param timestamp
	 *            the timestamp in milliseconds
	 * @param value
	 *            the observed integer value
	 */
	public HolidayObservation(Timestamp timestamp, int value) {
		this.observedValue = value;
		this.timestamp = new Timestamp(DateUtils.truncate(timestamp, Calendar.DAY_OF_MONTH).getTime());
	}
	

	@Override
	public Timestamp getTimestamp() {
		return this.timestamp;
	}

	@Override
	public void setTimestamp(Timestamp timestamp) {
		this.timestamp = new Timestamp(DateUtils.truncate(timestamp,
				Calendar.DAY_OF_MONTH).getTime());
		
	}

	@Override
	public int getObservedValue() {
		return this.observedValue;
	}

	@Override
	public void setObservedValue(int observedValue) {
		this.observedValue = observedValue;
		
	}
	@Override
	public String toString(){
		StringBuilder sb= new StringBuilder();
		String nl = System.getProperty("line.separator");
		sb.append("holiday observed at: "+ this.timestamp + nl);
		sb.append("observed holiday id: "+ this.observedValue+ nl);
		return sb.toString();
	}



}
