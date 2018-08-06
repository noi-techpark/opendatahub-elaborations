package it.unibz.tsmodel.overlay.weather;


import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.MeteoObservation;
import it.unibz.tsmodel.domain.Observation;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

import org.apache.commons.lang3.time.DateUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import com.google.gson.Gson;
import com.google.gson.stream.JsonReader;

/**
 * @author mreinstadler This class is used to read the weather observations and
 *         weather predictions from OpenWeatherMap
 * 
 */
class OWMReader implements WeatherReader{
	private final static String PROXY = "localhost";
	private static final Log logger = LogFactory.getLog(OWMReader.class);
	private final static String METEO_PREDICTION_URL = "http://api.openweathermap.org/data/2.5/forecast?id=3181913&appid=f0a0f61e1a86d6918f02e9ea18d488da";
	private final static String METEO_HISTORY_URL = "http://api.openweathermap.org/data/2.5/history/city?id=3181913&type=day&appid=f0a0f61e1a86d6918f02e9ea18d488da";
	private static OWMReader instance;

	/**
	 * @param config the configuration of the application
	 * @return the list of {@link Observation} as predictions. In case it is not possible to 
	 * retrieve any weather predictions, an empty list is returned
	 * @throws IOException
	 */
	public List<MeteoObservation> getWeatherPredictions(TSModelConfig config) {
		logger.info(
				"Start reading weather predictions from OpenWeatherMap");
		OWMObservations observations = null;
		URL url = null;

		try {	
			url = new URL(METEO_PREDICTION_URL);
			//url = new URL("http", PROXY, 8080, METEO_PREDICTION_URL);
			URLConnection urlConnection = url.openConnection();
			urlConnection.setDoOutput(true);
			urlConnection.setAllowUserInteraction(false);
			InputStream inputStream;
			inputStream = urlConnection.getInputStream();
			BufferedReader r = new BufferedReader(new InputStreamReader(inputStream));
			JsonReader reader = new JsonReader(r);
			observations = new Gson().fromJson(reader, OWMObservations.class);
			logger.info(
					"Finish reading weather predictions from OpenWeatherMap");
		} catch (IOException e) {
			logger.warn(
					"No weather predictions could be read- proceed the process without weather predictions");
			return new ArrayList<MeteoObservation>();
		}
		return observations.getObservations();
	}

	//TODO change the methode without enddate
	/**
	 * @param fromDate
	 *            the date from when the meteo observations should be read
	 * @param config the configuration of the application
	 * @return the list of the storical weather information starting from the
	 *         specified date. In case nothing is available, an empty list is 
	 *         returned
	 * @throws InterruptedException
	 */
	//TODO: get Data from DB
	public List<MeteoObservation> getStoricalWeatherObservations( Calendar fromDate, TSModelConfig config){
		if(fromDate==null)
			return new ArrayList<MeteoObservation>();
		DateFormat sdf = new SimpleDateFormat();
		logger.info("Start reading weather history from OpenWeatherMap from "+ sdf.format(fromDate.getTime()));
		ArrayList<MeteoObservation> meteoObservations = new ArrayList<MeteoObservation>();
		Calendar fromWhen = DateUtils.truncate(fromDate, Calendar.HOUR_OF_DAY);
		while (fromWhen.before(Calendar.getInstance())) {
			StringBuilder urlStringBuilder = new StringBuilder(
					METEO_HISTORY_URL);
			urlStringBuilder.append("&start=" + fromWhen.getTimeInMillis()
					/ 1000);
			
			Calendar toDate = Calendar.getInstance();
			toDate.setTime(fromWhen.getTime());
			toDate.add(Calendar.HOUR_OF_DAY, 23);
			urlStringBuilder.append("&end=" + toDate.getTimeInMillis() / 1000);
			URL url;
			try {
				url= new URL(urlStringBuilder.toString());
				//url = new URL("http", PROXY, 8080, urlStringBuilder.toString());
				URLConnection urlConnection = url.openConnection();
				urlConnection.setDoOutput(true);
				urlConnection.setAllowUserInteraction(false);
				InputStream inputStream = urlConnection.getInputStream();
				BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
				JsonReader reader = new JsonReader(bufferedReader);
				OWMObservations owmObservations = new Gson().fromJson(reader,
						OWMObservations.class);
				if(owmObservations.getObservations().isEmpty()){
					logger.info("no meteo observations from available. try manually "+ urlStringBuilder.toString());
					fromWhen.add(Calendar.HOUR_OF_DAY, 1);
				}
				else{
					for (MeteoObservation observation : owmObservations.getObservations())
						meteoObservations.add(observation);
					fromWhen.add(Calendar.DAY_OF_YEAR, 1);
				}
				
			} catch (IOException e) {
				logger.warn(
						"Error while looking for meteo observations from "+ sdf.format(fromWhen.getTime())+
						" to " + sdf.format(toDate.getTime()));
				return meteoObservations;
			}
		}
		logger.info(
				"Finish reading weather history from OpenWeatherMap- added "+ meteoObservations.size() + " new meteo observations");
		return meteoObservations;
	}
	public static WeatherReader getInstance() {
		if (instance == null)
			instance = new OWMReader();
		return instance;
	}

}
