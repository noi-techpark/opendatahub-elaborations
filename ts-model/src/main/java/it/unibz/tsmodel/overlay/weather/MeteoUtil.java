package it.unibz.tsmodel.overlay.weather;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.dao.MeteoObservationDao;
import it.unibz.tsmodel.domain.MeteoObservation;
import it.unibz.tsmodel.domain.Observation;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.HashMap;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;

/**
 * @author mreinstadler This class is used to generate meteo observations in the
 *         past and meteo predictions
 * 
 */
public class MeteoUtil {

	private final Log logger = LogFactory.getLog(MeteoUtil.class);

	@Autowired
	private MeteoObservationDao meteoObservationDaoDao;
	@Autowired
	private TSModelConfig config;

	/**
	 * this method reads the saved weather {@link Observation}, identifies the
	 * date of the last {@link Observation} (in case there does not exist any
	 * last obvervation, this date is set to the startdate defined in the
	 * {@link TSModelConfig} object), looks for new weather {@link Observation}
	 * and generates a hashmap with all the past observations
	 * 
	 * @return the list of all past {@link Observation} with the timestamp as
	 *         key and the {@link MeteoObservation} as value
	 */
	public  HashMap<Timestamp, MeteoObservation> getPastObservations() {
		logger.info("Start create Hashmap with weather observations and predictions of Bolzano");
		HashMap<Timestamp, MeteoObservation> observations = new HashMap<Timestamp, MeteoObservation>();
		Calendar cal = Calendar.getInstance();
		cal.add(Calendar.DAY_OF_YEAR, - config.getMaxHistoryDays());
		List<MeteoObservation> pastObservations = meteoObservationDaoDao
				.findObservations(new Timestamp(cal.getTimeInMillis()));
		retrieveAndSaveLastStoricalData(pastObservations);
		for (MeteoObservation observation : pastObservations) {
			observations.put(observation.getTimestamp(), observation);
		}
		
		logger.info("Finish to create Hashmap with weather observations + predictions of Bolzano");
		return observations;

	}

	/**
	 * this methode puts the weather predictions in the list of storical weather
	 * {@link Observation} in order to have one list of observations and
	 * predictions
	 */
	public void addWeatherPredictions(
			 HashMap<Timestamp, MeteoObservation> historyObservations) {
		WeatherReader reader = OWMReader.getInstance();
		List<MeteoObservation> observations = reader.getWeatherPredictions(this.config);
		for (MeteoObservation observation : observations) {
			if (observation.getObservedValue() > 0
					&& !historyObservations.containsKey(observation
							.getTimestamp())) {
				historyObservations
						.put(observation.getTimestamp(), observation);
			}
		}
	}

	/**
	 * this method checks if OpenWeatherMap has new storical {@link Observation}
	 * available and saves them to file/databas and to the input list at the
	 * same time
	 * 
	 * @param savedObservations
	 *            the list of saved {@link MeteoObservation}
	 */
	private void retrieveAndSaveLastStoricalData(List<MeteoObservation> savedObservations) {
		Calendar lastDate = Calendar.getInstance();
		if (savedObservations== null || savedObservations.isEmpty()){

			savedObservations= new ArrayList<MeteoObservation>();
			lastDate.setTime(this.config.getAppStartDate());
		}
		else {
			Timestamp soTimestamp = savedObservations.get(savedObservations.size()-1).getTimestamp();
			lastDate.add(Calendar.DATE, -365);
			if (soTimestamp.before(lastDate.getTime()))
				soTimestamp.setTime(lastDate.getTime().getTime());
			lastDate.setTime(soTimestamp);
			lastDate.add(Calendar.HOUR_OF_DAY, 1);
		}
		List<MeteoObservation> newObservations = null;
		Timestamp now = new Timestamp(Calendar.getInstance().getTimeInMillis());
		WeatherReader reader = IntegreenWeatherReader.getInstance(); 
		newObservations = reader.getStoricalWeatherObservations(lastDate, this.config);
		int savecount=0;
		for (MeteoObservation newObservation : newObservations) {
			if (savedObservations.isEmpty() ||
					newObservation.getTimestamp().after(savedObservations.
							get(savedObservations.size()-1).getTimestamp())) {
				
				if(now.after(newObservation.getTimestamp())){
					try{
					meteoObservationDaoDao.persist(newObservation);
					}catch(Exception ex){
						ex.printStackTrace();
						continue;
					}
					savecount++;
					savedObservations.add(newObservation);
				}
				
			}

		}
		logger.info(savecount + " new weather observatios saved to database");
	}

	/**
	 * @return the meteoObservationDaoDao
	 */
	public MeteoObservationDao getMeteoObservationDaoDao() {
		return meteoObservationDaoDao;
	}

	/**
	 * @param meteoObservationDaoDao
	 *            the meteoObservationDaoDao to set
	 */
	public void setMeteoObservationDaoDao(
			MeteoObservationDao meteoObservationDaoDao) {
		this.meteoObservationDaoDao = meteoObservationDaoDao;
	}

}
