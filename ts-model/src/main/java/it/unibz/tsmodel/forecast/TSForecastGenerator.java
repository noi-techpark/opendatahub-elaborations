// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.forecast;

import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.domain.ParkingObservation;


/**
 * @author mreinstadler this interface is implemented by classes that make
 *         predictions for free slots and save those predictions to a XML file
 *         The classes implementing this interface will run as cronjobs each
 *         hour to rebuild the predicitions each hour freshly
 * 
 */
public interface TSForecastGenerator {
	/**
	 * this makes a prediction for all the parking places by building (or using
	 * the current) models and then predicting free slots in the future. All the
	 * predictions are saved in the appropriate forecast.xml file
	 * @param periodicity the time distance between {@link ParkingObservation}
	 **/
	void predictAllFreeSlots(ObservationPeriodicity periodicity) throws Exception;

}
