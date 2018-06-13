package it.unibz.tsforecast.xml;
import it.unibz.tsforecast.configuration.TSForecastConfig;
import it.unibz.tsforecast.domain.ForecastStep;
import it.unibz.tsforecast.domain.ForecastSteps;
import it.unibz.tsforecast.domain.ParkingForecast;
import it.unibz.tsforecast.domain.ParkingForecasts;
import it.unibz.tsforecast.domain.ParkingPrediction;
import it.unibz.tsforecast.entity.ObservationPeriodicity;

import java.io.File;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.logging.Level;
import java.util.logging.Logger;

import com.thoughtworks.xstream.XStream;
import com.thoughtworks.xstream.io.xml.DomDriver;

/**
 * @author mreinstadler This class is responsible for the serialization and
 *         deserialization of forecasts to and from XML
 * 
 */
public class ForecastXMLDeserializer {
	private final static Logger logger = Logger.getLogger("ts-forecast");
	private ForecastSteps allForecasts = null;
	private XStream xstream = null;
	private TSForecastConfig config;

	
	
	/**
	 * initializes the xStream
	 */
	public ForecastXMLDeserializer(TSForecastConfig config){
		this.xstream = new XStream(new DomDriver());
		this.xstream.autodetectAnnotations(true);
		this.xstream.processAnnotations(ForecastSteps.class);
		this.config = config;
		
	}
	
	
	/**
	 * this reads the XML from file and initializes the list of 
	 * {@link ForecastStep}  
	 * @param periodicity the distance between the parking observations
	 * @param config the configuration of the application
	 */
	private void deserializeForecastInstances(ObservationPeriodicity periodicity) {
		File forecastFile = new File(config.getForecastDirectory()+ 
				File.separator + "forecast_" +periodicity+".xml");
		this.allForecasts = (ForecastSteps) this.xstream.fromXML(forecastFile);
		
	}
	
	/**
	 * @param periodicity the distance between the parking observations
	 * @return the complete list of forecasts as {@link ForecastSteps} object
	 */
	public ForecastSteps getForecasSteps(ObservationPeriodicity periodicity){
		if(this.allForecasts== null)
			deserializeForecastInstances(periodicity);
		return this.allForecasts;
	}
	
	/**
	 * @return the configured {@link XStream} xml streamer
	 */
	public XStream getConfiguredStreamer(){
		return this.xstream;
	}
	/**
	 * @param periodicity the distance between the parking observations
	 * @param forecastDate the date of the required forecast. Make sure that
	 * this date is not larger than the predefined steps of forecasts from now
	 * @return one {@link ForecastStep} for the required hour
	 */
	public ForecastStep getForecastStep(ObservationPeriodicity periodicity, Calendar forecastDate){
		ForecastStep step = null;
		if(this.allForecasts== null)
			deserializeForecastInstances(periodicity);
		if(this.allForecasts== null){
			logger.log(Level.WARNING, "The deserialization resulted in null");
			return null;
		}
		ArrayList<ForecastStep> steps = this.allForecasts.getForecastInstances();
		if(steps == null || steps.size()==0){
			logger.log(Level.WARNING, "The deserialization resulted in empty forecasts");
			return null;
		}
		if(steps.get(steps.size()-1).getForecastEndDate().before(forecastDate.getTime())){
			logger.log(Level.WARNING, "No forecasts found for the specified date. check the input date"
					+ "and the forecast.xml file");
			return null;
		}
		step = steps.get(0);
		for (ForecastStep forecastStep : steps) {
			if(forecastStep.getForecastEndDate().before(forecastDate.getTime()))
				step = forecastStep;
			else
				return step;
		}
		return step;
		
	}
	
	/**
	 * @param periodicity the time distance between parking observations
	 * @param parkingId the id of the parking lot
	 * @return the list of predictions for the required parking lot
	 */
	public ParkingForecasts getForecastsPerParkingLot(ObservationPeriodicity periodicity, String parkingId){
		ParkingForecasts result = new ParkingForecasts();
		if(this.allForecasts== null)
			deserializeForecastInstances(periodicity);
		if(this.allForecasts== null || this.allForecasts.getForecastInstances()==null){
			logger.log(Level.WARNING, "The deserialization was not possible");
			return null;
		}
		for(ForecastStep step: this.allForecasts.getForecastInstances()){
			for(ParkingPrediction prediction: step.getParkingPredictions()){
				if(String.valueOf(prediction.getParkingPlace().getParkingId()).equals(parkingId)){
					ParkingForecast forec = new ParkingForecast(prediction, step.getForecastStartDate(), step.getForecastEndDate());
					result.addOneParkingforecast(forec);
				}
			}
		}
		return result;
		
	}
	

}
