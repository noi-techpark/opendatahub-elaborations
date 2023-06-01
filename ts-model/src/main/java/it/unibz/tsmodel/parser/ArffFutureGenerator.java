// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.parser;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.Observation;
import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.domain.ParkingObservation;
import it.unibz.tsmodel.overlay.OverlayAttribute;
import it.unibz.tsmodel.overlay.OverlayAttributes;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

import org.apache.commons.lang3.time.DateUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/**
 * @author mreinstadler this class is used to create an arff string with future
 *         elements used for the prediction in a multivariate timeseries (with
 *         overlay data).
 */
class ArffFutureGenerator extends ArffStringGenerator {

	private final Log logger = LogFactory.getLog(ArffFutureGenerator.class);
	private ArffPreprocessor processor;
	private ObservationPeriodicity periodicity= ObservationPeriodicity.HOURLY;
	private ArrayList<Timestamp> futureDates;
	private TSModelConfig config;

	/**
	 * @param periodicity the time distance between {@link ParkingObservation}
	 * @param config the configuration of the Application
	 */
	public ArffFutureGenerator( ObservationPeriodicity periodicity,  TSModelConfig config) {
		this.processor = new ArffPreprocessor();
		this.periodicity = periodicity;
		this.futureDates = new ArrayList<Timestamp>();
		this.config = config;
	}

	@Override
	public String generateArff( List<ParkingObservation> observations,
			 OverlayAttributes overlayAttrs) {
		logger.info("Generating arff String for forecasts with "
				+ config.getForecastSteps() + " instances");
		this.futureDates.clear();
		StringBuilder arffStringBuilder = new StringBuilder();
		processor.addArffHeader(arffStringBuilder, overlayAttrs);
		addFutureEmptyInstances(overlayAttrs, arffStringBuilder);
		logger.info("Finish generating future arff string");
		return arffStringBuilder.toString();
	}

	/**
	 * Adds [newInstances] future elements start in from the current date with
	 * empty freeSlots (used for prediction) This is required by WEKA, otherwise
	 * the prediction cannot be done.
	 * 
	 * @param overlayAttrs
	 *            the list of {@link OverlayAttribute}
	 * @param stringBuilder
	 *            the current .arff string in form of a {@link StringBuilder} object
	 */
	private void addFutureEmptyInstances( OverlayAttributes overlayAttrs,
			  StringBuilder stringBuilder) {
		Calendar instanceDate = DateUtils.truncate(Calendar.getInstance(), Calendar.MINUTE);
		while(instanceDate.get(Calendar.MINUTE)%periodicity.minutes() != 0)
			instanceDate.add(Calendar.MINUTE, 1);
		for (int a = 0; a < config.getForecastSteps(); a++) {
			
			Timestamp instanceTimestamp = new Timestamp(instanceDate.getTimeInMillis());
			Observation observation = new ParkingObservation(instanceTimestamp, -1,null);
			this.futureDates.add(instanceTimestamp);
			processor.addSingleArffInstance(stringBuilder, observation, overlayAttrs, config);
			instanceDate.add(Calendar.MINUTE, this.periodicity.minutes());
		}

	}

	/**
	 * @return the list of {@link Timestamp} used for the future predictions
	 */
	public ArrayList<Timestamp> getFutureDates() {
		return futureDates;
	}
	

	
}
