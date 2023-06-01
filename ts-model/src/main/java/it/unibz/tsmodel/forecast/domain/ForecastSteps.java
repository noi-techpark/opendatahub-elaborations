// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.forecast.domain;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Calendar;

import org.apache.commons.lang3.time.DateUtils;

import com.thoughtworks.xstream.annotations.XStreamAlias;


/**
 * @author mreinstadler This class holds several items of type
 *         {@link ForecastStep} and a date, whitch corresponds to the date when
 *         the forecasts were calculated (time when this class is instantiated)
 */
@XStreamAlias("full-forecast")
public class ForecastSteps {
	@XStreamAlias("computation-time")
	private Timestamp timestamp;
	@XStreamAlias("forecast-instances")
	private ArrayList<ForecastStep> forecstInstances = null;

	/**
	 * @return the date when the forecasts were calculated
	 */
	public Timestamp getTimestamp() {
		return this.timestamp;
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

}
