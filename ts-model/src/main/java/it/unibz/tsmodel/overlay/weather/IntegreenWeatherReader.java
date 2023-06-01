// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.overlay.weather;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.MeteoObservation;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.reflect.Type;
import java.net.URL;
import java.net.URLConnection;
import java.sql.Timestamp;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.time.DateUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import com.google.gson.stream.JsonReader;

public class IntegreenWeatherReader implements WeatherReader{

	private static final Log logger = LogFactory.getLog(OWMReader.class);
	private static final String METEO_HISTORY_URL = "http://ipchannels.integreen-life.bz.it/MeteoFrontEnd/rest/get-records-in-timeframe?station=83200MS&name=precipitation";
	private static IntegreenWeatherReader instance;

	@Override
	public List<MeteoObservation> getWeatherPredictions(TSModelConfig config) {
		//TODO: Implement action as soon as service will be available
		return null;
	}

	@Override
	public List<MeteoObservation> getStoricalWeatherObservations(
			Calendar fromDate, TSModelConfig config) {
		if(fromDate==null)
			return new ArrayList<MeteoObservation>();
		DateFormat sdf = new SimpleDateFormat();
		logger.info("Start reading weather history from Integreen from "+ sdf.format(fromDate.getTime()));
		List<MeteoObservation> meteoObservations = new ArrayList<MeteoObservation>();
		Calendar fromWhen = DateUtils.truncate(fromDate, Calendar.HOUR_OF_DAY);
		while (fromWhen.before(Calendar.getInstance())) {
			StringBuilder urlStringBuilder = new StringBuilder(
					METEO_HISTORY_URL);
			urlStringBuilder.append("&from=" + fromWhen.getTimeInMillis());
			
			Calendar toDate = Calendar.getInstance();
			toDate.setTime(fromWhen.getTime());
			toDate.add(Calendar.HOUR_OF_DAY, 23);
			urlStringBuilder.append("&to=" + toDate.getTimeInMillis());
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
				Type listType = new TypeToken<ArrayList<IntegreenObservation>>() {}.getType();
				List<IntegreenObservation> integreenObservations = new Gson().fromJson(reader,
						listType);
				if(integreenObservations.isEmpty()){
					logger.info("no meteo observations from available. try manually "+ urlStringBuilder.toString());
					fromWhen.add(Calendar.HOUR_OF_DAY, 1);
				}
				else{
					Map<Long, Double> subSetForHour = getPerHourObservation(integreenObservations);
					for (Map.Entry<Long, Double> entry: subSetForHour.entrySet())
						meteoObservations.add(new MeteoObservation(new Timestamp(entry.getKey()), new Double(10.*entry.getValue()).intValue()));
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

	private Map<Long, Double> getPerHourObservation(
			List<IntegreenObservation> integreenObservations) {
		Map<Long, Double> sums = new LinkedHashMap<Long, Double>();
		for(IntegreenObservation obsv:integreenObservations){
			Date hour = DateUtils.truncate(new Date(obsv.getTimestamp()), Calendar.HOUR_OF_DAY);
			Double value = sums.get(hour.getTime());
			if (value != null)
				value += obsv.getValue();
			else 
					value = obsv.getValue();
			sums.put(hour.getTime(), value);
		}
		return sums;
	}

	public static WeatherReader getInstance() {
		if (instance == null)
			instance = new IntegreenWeatherReader();
		return instance;
	}

}
