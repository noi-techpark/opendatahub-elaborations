package it.unibz.tsmodel.domain;

import java.sql.Timestamp;
import java.util.Calendar;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;

import org.apache.commons.lang3.time.DateUtils;

/**
 * @author mreinstadler This class represents one event observation stored in
 *         the DB. The timestamp is the primary key and the observed the foreign
 *         key to the event record. The timestamp is daily with hours, minutes,
 *         seconds and milliseconds zero
 * 
 */
@Entity
public class EventObservation implements Observation {

	@Id
	private Timestamp timestamp;
	@Column(name = "event_id")
	private int observedValue = -1;
	
	public EventObservation(){
		
	}
	/**
	 * * This creates a new object by truncating the timestamp with hour=0,
	 * minute=0, seconds=0 and milliseconds = 0
	 * 
	 * @param timestamp
	 *            the timestamp in milliseconds
	 * @param value
	 *            the observed integer value
	 */
	public EventObservation(Timestamp timestamp, int value) {
		this.observedValue = value;
		this.timestamp = new Timestamp(DateUtils.truncate(timestamp,
				Calendar.DAY_OF_MONTH).getTime());
	}

	@Override
	public Timestamp getTimestamp() {
		return timestamp;
	}

	@Override
	public void setTimestamp(Timestamp timestamp) {
		this.timestamp = new Timestamp(DateUtils.truncate(timestamp,
				Calendar.DAY_OF_MONTH).getTime());
	}

	@Override
	public int getObservedValue() {
		return observedValue;
	}

	@Override
	public void setObservedValue(int observedValue) {
		this.observedValue = observedValue;
	}
	
	@Override
	public String toString(){
		StringBuilder sb= new StringBuilder();
		String nl = System.getProperty("line.separator");
		sb.append("event observed at: "+ this.timestamp + nl);
		sb.append("observed event id: "+ this.observedValue+ nl);
		return sb.toString();
	}


}
