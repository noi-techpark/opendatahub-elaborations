package it.unibz.tsforecast.domain;

import flexjson.JSONSerializer;
import it.unibz.tsforecast.entity.Event;
import it.unibz.tsforecast.entity.Holiday;
import it.unibz.tsforecast.entity.ObservationMetaInfo;
import it.unibz.tsforecast.entity.ObservationPeriodicity;
import it.unibz.tsforecast.entity.ParkingPlace;
import it.unibz.tsforecast.entity.Weather;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Calendar;

import com.thoughtworks.xstream.annotations.XStreamAlias;

/**
 * @author mreinstadler This class represents one step of forecast (e.g. if the 
 * periodicity is hourly, then it represents one full hour) with the weather, events, 
 * holidays and the list of {@link ParkingPrediction}: for each
 *  {@link ParkingPlace} one {@link TSPrediction}
 */

@XStreamAlias("forecast-instance")
public class ForecastStep {
	@XStreamAlias("forecast-startdate")
	private Timestamp forecastStartDate;
	@XStreamAlias("forecast-enddate")
	private Timestamp forecastEndDate;
	private Weather weather= null;
	private Holiday holiday = null;
	private Event event = null;
	@XStreamAlias("parking-predictions")
	private ArrayList<ParkingPrediction> parkingPredictions = null;
	
	

	

	/**
	 * this initializes the ForecastStep 
	 * @param startDate
	 *            the timestamp from when the forecast is valid
	 * @param metaInformatinos
	 *            the meta information about the forecast
	 * @param parkingPredictions the
	 *            list of {@link ParkingPrediction}
	 * @param periodicity the time distance between {@link ParkingObservation}
	 */
	public ForecastStep(Timestamp startDate,ArrayList<ObservationMetaInfo> metaInformatinos,
			ArrayList<ParkingPrediction> parkingPredictions, ObservationPeriodicity periodicity) {
		this.forecastStartDate = startDate;
		Calendar cal = Calendar.getInstance();
		cal.setTime(startDate);
		cal.add(Calendar.MINUTE, periodicity.minutes());
		this.forecastEndDate = new Timestamp(cal.getTimeInMillis());
		this.parkingPredictions = parkingPredictions;
		for(ObservationMetaInfo metaInfo: metaInformatinos){
			if(metaInfo.getClass().equals(Weather.class))
				this.weather = (Weather)metaInfo;
			else if(metaInfo.getClass().equals(Event.class))
				this.event = (Event)metaInfo;
			else if(metaInfo.getClass().equals(Holiday.class))
				this.holiday = (Holiday)metaInfo;
		}
	
	}

	/**
	 * this initializes the ForecastHour
	 * @param startDate
	 *            the timestamp of the forecast 
	 * @param metaInformations
	 *            the meta information about this forecast hour
	 * @param periodicity the time distance between {@link ParkingObservation}
	 */
	public ForecastStep(Timestamp startDate, ArrayList<ObservationMetaInfo> metaInformations, 
			ObservationPeriodicity periodicity) {
		this.forecastStartDate = startDate;
		Calendar cal = Calendar.getInstance();
		cal.setTime(startDate);
		cal.add(Calendar.MINUTE, periodicity.minutes());
		this.forecastEndDate = new Timestamp(cal.getTimeInMillis());
		for(ObservationMetaInfo metaInfo: metaInformations){
			if(metaInfo.getClass().equals(Weather.class))
				this.weather = (Weather)metaInfo;
			else if(metaInfo.getClass().equals(Event.class))
				this.event = (Event)metaInfo;
			else if(metaInfo.getClass().equals(Holiday.class))
				this.holiday = (Holiday)metaInfo;
		}
		this.parkingPredictions = new ArrayList<ParkingPrediction>();
	}


	


	/**
	 * @param parkingPrediction
	 *            one single {@link ParkingPrediction} to be added to the list
	 *            of Parkingpredictions
	 */
	public void addOneParkingPrediction(ParkingPrediction parkingPrediction) {
		this.parkingPredictions.add(parkingPrediction);
	}

	/**
	 * @param metaInformations
	 *            the list of meta information of the hour of forecast
	 */
	public void setMetaData(ArrayList<ObservationMetaInfo> metaInformations) {
		for(ObservationMetaInfo metaInformatin: metaInformations){
			if(metaInformatin.getClass().equals(Weather.class))
				this.weather = (Weather)metaInformatin;
			else if(metaInformatin.getClass().equals(Event.class))
				this.event = (Event)metaInformatin;
			else if(metaInformatin.getClass().equals(Holiday.class))
				this.holiday = (Holiday)metaInformatin;
		}
	}

	/**
	 * this sets the date of the forecast hour
	 * @param timestamp
	 *            the timestamp of the forecast
	 */
	public void setForecastStartDate(Timestamp timestamp) {
		this.forecastStartDate = timestamp;
	}
	/**
	 * @return the timestamp of the forecast
	 */
	public Timestamp getForecastStartDate() {
		return forecastStartDate;
	}
	
	
	
	/**
	 * @return the forecastEndDate
	 */
	public Timestamp getForecastEndDate() {
		return forecastEndDate;
	}

	/**
	 * @param forecastEndDate the forecastEndDate to set
	 */
	public void setForecastEndDate(Timestamp forecastEndDate) {
		this.forecastEndDate = forecastEndDate;
	}

	/**
	 * @return the weather
	 */
	public Weather getWeather() {
		return weather;
	}

	/**
	 * @param weather the weather to set
	 */
	public void setWeather(Weather weather) {
		this.weather = weather;
	}

	/**
	 * @return the holiday
	 */
	public Holiday getHoliday() {
		return holiday;
	}

	/**
	 * @param holiday the holiday to set
	 */
	public void setHoliday(Holiday holiday) {
		this.holiday = holiday;
	}

	/**
	 * @return the event
	 */
	public Event getEvent() {
		return event;
	}

	/**
	 * @param event the event to set
	 */
	public void setEvent(Event event) {
		this.event = event;
	}

	/**
	 * @return the parkingPredictions
	 */
	public ArrayList<ParkingPrediction> getParkingPredictions() {
		return parkingPredictions;
	}

	/**
	 * @param parkingPredictions the parkingPredictions to set
	 */
	public void setParkingPredictions(
			ArrayList<ParkingPrediction> parkingPredictions) {
		this.parkingPredictions = parkingPredictions;
	}

	/**
	 * @return a string in JSON format. It includes the list of {@link ParkingObservation}, which 
	 * is essential for the final result
	 */
	public String forecaststepToJSON(){
		return new JSONSerializer().exclude("*.class").include("parkingPredictions").serialize(this);
	}
	
	
	
	
	

}
