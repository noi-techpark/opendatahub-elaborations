package it.unibz.tsmodel.domain;

import it.unibz.tsmodel.overlay.weather.Weather;

import java.sql.Timestamp;
import java.util.Calendar;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Transient;

import org.apache.commons.lang3.time.DateUtils;
/**
 * @author mreinstadler
 * This class represents one meteo observation stored in 
 * the DB. The timestamp is the primary key and the observed
 * the foreign key to the meteo record. The timestamp is hourly
 * with minutes, seconds and milliseconds zero
 *
 */
@Entity
public class MeteoObservation implements Observation {
	
	@Column(name = "meteo_id")
	private int observedValue = -1;
	@Id
	private Timestamp timestamp;
	@Transient
	private Weather metaInformation= null;
	

	public MeteoObservation(){
		
	}
	/**
	 * this initializes a new Meteoobservation by assuring that
	 * the minutes, seconds and milliseconds of the observation 
	 * are set to 0
	 * @param timestamp
	 *            the timestamp in milliseconds
	 * @param value
	 *            the observed integer value
	 */
	public MeteoObservation(Timestamp timestamp, int value) {
		this.observedValue = value;
		this.timestamp = new Timestamp(DateUtils.truncate(timestamp, Calendar.HOUR_OF_DAY).getTime());
		metaInformation = new Weather();
	}
	
	
	@Override
	public Timestamp getTimestamp() {
		return this.timestamp;
	}

	@Override
	public void setTimestamp(Timestamp timestamp) {
		this.timestamp = new Timestamp(DateUtils.truncate(timestamp, Calendar.HOUR_OF_DAY).getTime());
		
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
	 * @param metaInformation the metaInformation to set
	 */
	public void setMetaInformation(Weather metaInformation) {
		this.metaInformation = metaInformation;
	}

	/**
	 * @return the {@link Weather} as {@link ObservationMetaInfo}
	 */
	public Weather getMetaInformation(){
		return this.metaInformation;
	}

	@Override
	public String toString(){
		StringBuilder sb= new StringBuilder();
		String nl = System.getProperty("line.separator");
		sb.append("weather observed at: "+ this.timestamp + nl);
		sb.append("observed weather code: "+ this.observedValue+ nl);
		return sb.toString();
	}



}
