// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsforecast.domain;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Calendar;

import org.apache.commons.lang3.time.DateUtils;

import com.thoughtworks.xstream.annotations.XStreamAlias;

import flexjson.JSON;
import flexjson.JSONSerializer;

/**
 * @author mreinstadler This class holds several items of type
 *         {@link ForecastStep} and a date, whitch corresponds to the date when
 *         the forecasts were calculated (time when this class is instantiated)
 */
@XStreamAlias("full-forecast")
public class ForecastSteps {
	@XStreamAlias("computation-time")
	private Timestamp timestamp= null;
	@XStreamAlias("forecast-instances")
	private ArrayList<ForecastStep> forecstInstances = null;

	
	public ForecastSteps(){
		this.forecstInstances = new ArrayList<ForecastStep>();
	}
	/**
	 * @return the date when the forecasts were calculated
	 */
	public Timestamp getTimestamp() {
		return this.timestamp;
	}
	

	/**
	 * @return the list of {@link ForecastStep}
	 */
	@JSON(include=true)
	public ArrayList<ForecastStep> getForecastInstances() {
		return forecstInstances;

	}

	/**
	 * @param forecastInstances
	 *            the list of {@link ForecastStep}
	 */
	public void setForecastInstances(ArrayList<ForecastStep> forecastInstances) {
		this.forecstInstances = forecastInstances;
	}

	/**
	 * this initiates the object by setting the date to the current date with
	 * minutes, seconds and milliseconds to 0
	 * 
	 * @param forecastInstances
	 *            the list of {@link ForecastStep}
	 */
	public ForecastSteps(ArrayList<ForecastStep> forecastInstances) {
		this.forecstInstances = forecastInstances;
		this.timestamp = new Timestamp(DateUtils.
				truncate(Calendar.getInstance(), Calendar.HOUR_OF_DAY).getTimeInMillis());
	}
	//TODO serialize the collection
	/**
	 * @return a string in JSON format. It includes the list of {@link ForecastStep}
	 */
	public String toJSON(){
		return new JSONSerializer().exclude("*.class").include("forecstInstances").serialize(this);
	}

}
