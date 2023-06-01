// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.parser;

import it.unibz.tsmodel.domain.Observation;
import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.domain.ParkingObservation;
import it.unibz.tsmodel.overlay.OverlayAttribute;
import it.unibz.tsmodel.overlay.OverlayAttributes;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import weka.classifiers.timeseries.core.TSLagMaker.Periodicity;

/**
 * This interface is implemented by the different .arff parsers (arff parser
 * which creates univariate timeseries without {@link OverlayAttribute} and arff
 * parser for multivariate timeseries including {@link OverlayAttribute})
 * 
 * @author mreinstadler
 * 
 */
abstract class ArffStringGenerator {
	private final Log logger = LogFactory.getLog(ArffStringGenerator.class);

	/**
	 * creates an String in .arff format, which can be analyzed by WEKA the
	 * final String contains instances of the TIS {@link Observation} in hourly
	 * periodicity and the possible values of {@link OverlayAttribute} (if the
	 * timeseries is multivariate)
	 * 
	 * @param the
	 *            list of storical {@link ParkingObservation} of a parking
	 *            place. In case a future String should be created, this can be
	 *            null
	 * @param overlayAttrs
	 *            the list of {@link OverlayAttribute} used to build the
	 *            timeseries timeseries. if the timeseries is only univariate,
	 *            this parameter can be null
	 * @return the String in .arff format. For documentation see weka.arff
	 */
	abstract String generateArff(
			 List<ParkingObservation> storicalParkingData,
			 OverlayAttributes overlayAttrs);

	
	
	/**
	 * this method filters the list of {@link ParkingObservation} by creating a new list. The resulting
	 * list contains the minimum value of free slots observed within the period.
	 * @param parkingObservations list of {@link ParkingObservation}
	 * which should be filtered with the specified {@link Periodicity} (e.g. only hourly observations, half hourly 
	 * observations or quarter hourly observations)
	 * @param periodicity the {@link ObservationPeriodicity} to filter the list of {@link ParkingObservation}
	 * @return the new list of {@link ParkingObservation} with the required periodicity
	 */
	public List<ParkingObservation> filterObservationsTimespan( List<ParkingObservation> parkingObservations,  ObservationPeriodicity periodicity){
		if (parkingObservations == null || parkingObservations.isEmpty()) {
			logger.info("no parking observation in the list- no filtering applied");
			return parkingObservations;
		}
		logger.info("filter the observations on "+periodicity +" basis");
		ArrayList<ParkingObservation> newObservations = new ArrayList<ParkingObservation>();
		ParkingObservation firstObservation = parkingObservations.get(0);
		firstObservation.setMinutesSecondsZero();
		parkingObservations.remove(0);
		int initialSize = parkingObservations.size();
		for (ParkingObservation currentObservation : parkingObservations) {
			long currMinutes = currentObservation.getTimestamp().getTime()/60000;
			if(currMinutes % periodicity.minutes() ==0){
				newObservations.add(firstObservation);
				firstObservation = currentObservation;
			}else if (currentObservation.getObservedValue() < firstObservation
					.getObservedValue())
				firstObservation.setObservedValue(currentObservation.getObservedValue());	
		}
		newObservations.add(firstObservation);
		logger.info("from original "+ initialSize+" observations remained "+ newObservations.size());
		return newObservations;
	}
	

}
