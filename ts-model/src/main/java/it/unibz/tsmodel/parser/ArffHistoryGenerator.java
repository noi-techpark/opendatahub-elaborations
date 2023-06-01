// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.parser;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.Observation;
import it.unibz.tsmodel.domain.ParkingObservation;
import it.unibz.tsmodel.overlay.OverlayAttribute;
import it.unibz.tsmodel.overlay.OverlayAttributes;

import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/**
 * This class is used to generate an .arff String from the original JSON string.
 * The final .arff string contains several overlay attributes defined in the
 * {@link OverlayAttributeCollector} class
 * 
 * @author mreinstadler
 * 
 */
class ArffHistoryGenerator extends ArffStringGenerator {

	private final Log logger = LogFactory.getLog(ArffHistoryGenerator.class);
	private TSModelConfig config;
	public ArffPreprocessor processor;
	

	public ArffHistoryGenerator(TSModelConfig config) {
		this.processor = new ArffPreprocessor();
		this.config = config;
	}

	@Override
	public String generateArff( List<ParkingObservation> parkingData,
			 OverlayAttributes overlayAttrs) {
		logger.info("Generating arff String with overlay attributes");
		StringBuilder arffStringBuilder = new StringBuilder();

		processor.addArffHeader(arffStringBuilder, overlayAttrs);

		if (parkingData != null)
			addAllArffInstances(arffStringBuilder, parkingData, overlayAttrs);
		logger.info("Finish generating arff String with overlay attributes");
		return arffStringBuilder.toString();
	}

	/**
	 * adds all the instances to the .arff formatted StringBuilder
	 * 
	 * @param stringBuilder
	 * @param observations
	 *            the list of free slots {@link ParkingObservation}
	 * @param overlayAttrs
	 *            the list of {@link OverlayAttribute}
	 */
	private void addAllArffInstances( StringBuilder stringBuilder,
			 List<ParkingObservation> observations,
			 OverlayAttributes overlayAttrs) {
		for (Observation observation : observations)
			processor.addSingleArffInstance(stringBuilder, observation, overlayAttrs, config);

	}

	
}
