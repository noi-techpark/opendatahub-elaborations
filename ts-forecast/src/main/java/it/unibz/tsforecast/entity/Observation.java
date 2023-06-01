// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsforecast.entity;

import java.sql.Timestamp;

/**
 * @author mreinstadler This interface is implemented by the different kinds of
 *         observations (e.g. parking-free-slots observation and
 *         meteo-observation)
 * 
 */
public interface Observation {

	/**
	 * @return the timestamp of the observation
	 */
	public Timestamp getTimestamp();

	/**
	 * @param timestamp
	 *            the timestamp in milliseconds
	 */
	public void setTimestamp(Timestamp timestamp);

	/**
	 * @return the observed value at a given time
	 */
	public int getObservedValue();

	/**
	 * @param observedValue
	 *            the observed value
	 */
	public void setObservedValue(int observedValue);
	
	
	public ObservationMetaInfo getMetaInformation();
	
	
	
	
	
	
	
	

}
