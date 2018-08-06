package it.unibz.tsmodel.domain;

import java.sql.Timestamp;
import java.util.Calendar;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;

import org.apache.commons.lang3.time.DateUtils;
import org.hibernate.annotations.GenericGenerator;

/**
 * @author mreinstadler
 * This class represents one parking observation stored in the DB. Timestamp and parking_id are
 * unique, the observed value represents the observed free slots at that time. 
 * The timestamp is expressed in 5 minutes (0,5,10,15,20,25,...) with seconds and 
 * nanoseconds zero. (This is due to guarantee an equi spaces time-series)
 */
@Entity
public class ParkingObservation implements Observation {
	@Id
	@GenericGenerator(name = "generator", strategy = "increment", parameters = {})
	@GeneratedValue(generator = "generator")
	@Column(name = "id")
	private long id;
	@Column(name = "freeslots")
	private int observedValue = -1;
	private Timestamp timestamp= null;
	private String parkingplace;

	public ParkingObservation(){	
	
	}

	/**
	 * Constructor, which assures that the time of the {@link Observation}
	 * is truncated to the next full 5 minutes (before)
	 * @param timestamp
	 *            the timestamp in milliseconds
	 * @param value
	 *            the observed integer value
	 */
	public ParkingObservation(Timestamp timestamp, int value, String parkingId) {
		this.observedValue = value;
		Calendar cal = Calendar.getInstance();
		cal.setTimeInMillis(timestamp.getTime());
		cal = DateUtils.truncate(cal, Calendar.MINUTE);
		while(cal.get(Calendar.MINUTE)%5 != 0)
			cal.add(Calendar.MINUTE, -1);
		this.timestamp = new Timestamp(cal.getTimeInMillis());
		this.parkingplace = parkingId;
		
	}

	/**
	 * this sets the minutes, seconds and nano seconds of the timestamp of the {@link ParkingObservation}
	 * to zero. E.g. 14.33.05 would result in 14.00.00
	 */
	public void setMinutesSecondsZero(){
		this.timestamp.setTime(DateUtils.truncate(this.timestamp, Calendar.HOUR_OF_DAY).getTime());
	}

	/**
	 * @return the parkingplace
	 */
	public String getParkingplace() {
		return parkingplace;
	}

	/**
	 * @param parkingplace the parkingplace to set
	 */
	public void setParkingplace(String parkingplace) {
		this.parkingplace = parkingplace;
	}
	@Override
	public Timestamp getTimestamp() {
		return this.timestamp;
	}

	@Override
	public void setTimestamp(Timestamp timestamp) {
		this.timestamp = timestamp;
		
	}

	@Override
	public int getObservedValue() {
		return this.observedValue;
	}

	@Override
	public void setObservedValue(int observedValue) {
		this.observedValue = observedValue;
		
	}
	/**
	 * @return the id
	 */
	public long getId() {
		return id;
	}

	/**
	 * @param id the id to set
	 */
	public void setId(long id) {
		this.id = id;
	}
	
	
	@Override
	public String toString(){
		String nl = System.getProperty("line.separator");
		StringBuilder sb = new StringBuilder();
		sb.append("parkinglot: "+ this.parkingplace + nl);
		sb.append("observed at: "+ this.timestamp+ nl);
		sb.append("freeSlots: "+ this.observedValue + nl);
		return sb.toString();
	}

}
