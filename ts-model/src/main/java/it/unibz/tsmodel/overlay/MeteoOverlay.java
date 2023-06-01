// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.overlay;

import it.unibz.tsmodel.domain.MeteoObservation;
import it.unibz.tsmodel.domain.Observation;
import it.unibz.tsmodel.domain.ObservationMetaInfo;
import it.unibz.tsmodel.overlay.weather.MeteoUtil;
import it.unibz.tsmodel.overlay.weather.Weather;

import java.sql.Timestamp;
import java.util.Calendar;
import java.util.HashMap;

import javax.annotation.PostConstruct;

import org.apache.commons.lang3.time.DateUtils;
import org.springframework.beans.factory.annotation.Autowired;

/**
 * @author mreinstadler This class represent one meteo observations or
 *         prediction used as overlay attribute in the weka prediction process
 * 
 */
class MeteoOverlay implements OverlayAttribute {

	private final String attrName = "meteo";
	private final String attrFormat = "Numeric";
	private HashMap<Timestamp, MeteoObservation> observationsAndPredictions = null;
	@Autowired
	private MeteoUtil meteoUtil;

	/**
	 * Constructs the meteo overlay by initializing the list of overlay values
	 * 
	 * @param meteoStragegy
	 *            the strategy used to calculate the meteo value
	 */
	@PostConstruct
	public void init() {
		this.observationsAndPredictions = meteoUtil.getPastObservations();
		meteoUtil.addWeatherPredictions(this.observationsAndPredictions);
	}

	@Override
	public String getAttributeName() {
		return this.attrName;
	}

	@Override
	public String getAttributeFormat() {
		return this.attrFormat;
	}

	@Override
	public String getAttributeValue(Timestamp timestamp, OverlayStrategy strategy) {
		String attrValue = "?";
		Timestamp time = new Timestamp(DateUtils.truncate(timestamp,
				Calendar.HOUR_OF_DAY).getTime());
		if (strategy == OverlayStrategy.REAL_VAL) {
			Observation observation = getNearestMeteoValue(time,
					observationsAndPredictions, -1);
			if (observation != null) {
				Integer a = observation.getObservedValue();
				attrValue = a.toString();
			}
		}
		else{
			attrValue = getBoolMeteoValue(time, 
					observationsAndPredictions).toString();
		}
		return attrValue;

	}

	/**
	 * this method retrieves the nearest weather observation for the required
	 * time. If there is no observation at exactly the required time in the
	 * list, the hour before is consulted... until 12 hours before
	 * 
	 * @param timestamp
	 *            the timestamp of the required observation
	 * @param observations
	 *            the list containing all the weather observations and
	 *            predictions
	 * @param hoursForOrBackward
	 *            the quantity of hours to look foreward (+) or backward (-)
	 * @param time
	 *            the time for the required observation
	 * @return the observation at or near to the required time, null if there
	 *         exists absolutely no observation
	 */
	private MeteoObservation getNearestMeteoValue(Timestamp timestamp,
			HashMap<Timestamp, MeteoObservation> observations,
			int hoursForOrBackward) {
		int index = 0;
		Calendar cal = Calendar.getInstance();
		cal.setTime(timestamp);
		while (index < 12) {
			if (!observations.containsKey(cal.getTime())) {
				cal.add(Calendar.HOUR_OF_DAY, hoursForOrBackward);
				index++;
			} else
				return observations.get(new Timestamp(cal.getTimeInMillis()));
		}
		return new MeteoObservation();

	}

	/**
	 * this calculates the rain or not rain value for the day by looking at the
	 * hours before the required date and returning 1 if there was an hour of
	 * rain (hours after 6 am). If the required date lies within 22-06 always 0
	 * is returned because rain has no impact on the free slots in a parking place
	 * 
	 * @param timestamp
	 *            the date of the parking observation
	 * @param observations
	 *            the meteo observations
	 * @return 1 if there was rain, 0 otherwise
	 */
	private Integer getBoolMeteoValue(Timestamp timestamp,
			HashMap<Timestamp, MeteoObservation> observations) {
		Calendar cal = Calendar.getInstance();
		cal.setTime(timestamp);
		int hour = cal.get(Calendar.HOUR_OF_DAY);
		if (hour > 22 || hour < 7)//because rain has no influence at night 
			return 0;
		int index =0;
		int maxIndex= 2;
		if(hour>9&& hour<6)
			maxIndex= 4;
		while (index<maxIndex) {
			if (observations.containsKey(cal.getTime())) {
				int val = observations.get(cal.getTime()).getObservedValue();
				if (val>5&& val<20)
					return 1;
			}
			index++;
			cal.add(Calendar.HOUR_OF_DAY, -1);
		}
		return 0;

	}

	@Override
	public ObservationMetaInfo getMetaInformation(Timestamp timestamp) {
		Timestamp time = new Timestamp(DateUtils.truncate(timestamp,
				Calendar.HOUR_OF_DAY).getTime());
		MeteoObservation obs = getNearestMeteoValue(time,
				observationsAndPredictions, +1);
		ObservationMetaInfo metaInfo= null;
		if(obs.getObservedValue() >-1)
			metaInfo = obs.getMetaInformation();
		else
			metaInfo= new Weather();
		return metaInfo;

	}

}
