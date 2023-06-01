// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.parser;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.Observation;
import it.unibz.tsmodel.overlay.OverlayAttribute;
import it.unibz.tsmodel.overlay.OverlayAttributes;

import java.sql.Timestamp;

/**
 * @author mreinstadler this helps in the arff creation process by providing
 *         methods for the arff header and the single arff instances
 * 
 */
class ArffPreprocessor {
	
	/**
	 * the attribute in the .arff string to be forecasted
	 */
	public final static String FORECASTATTRIBUTE = "freeSlots";

	/**
	 * the date attribute in the .arff string
	 */
	public final static String DATEATTRIBUTE = "timestamp";

	/**
	 * the attributes of the .arff file
	 */
	final static String RELATION = "freeParkingSlots";
	final static String ARFFATTRIBUTE = "@ATTRIBUTE";
	final static String ARFFNUMERIC = "NUMERIC";
	final static String ARFFDATE = "DATE \"yyyy-MM-dd\'T\'HH:mm\"";
	final static String ARFFRELATIONSECTION = "@relation";
	final static String ARFFDATASECTION = "@data";
	

	/**
	 * @param stringBuilder
	 *            the current arff string in form of a {@link StringBuilder}
	 * @param overlayAttributes
	 *            the list of {@link OverlayAttribute} to be included in the arff
	 *            header it is null, if the timeseries has no {@link OverlayAttribute}
	 *            (univariate timeseries)
	 */
	public void addArffHeader(StringBuilder stringBuilder,
			 OverlayAttributes overlayAttributes) {
		if(stringBuilder==null)
			stringBuilder= new StringBuilder();
		String lineseparator = System.getProperty("line.separator");
		stringBuilder.append(ARFFRELATIONSECTION + " " + RELATION + lineseparator);
		stringBuilder.append(ARFFATTRIBUTE + " " + FORECASTATTRIBUTE + " " + ARFFNUMERIC
				+ lineseparator);
		if (overlayAttributes!= null) {
			for (OverlayAttribute ol : overlayAttributes.getOverlayAttributes()) {
				String name = ol.getAttributeName();
				String format = ol.getAttributeFormat();
				stringBuilder.append(ARFFATTRIBUTE + " " + name + " " + format
						+ lineseparator);
			}
		}
		stringBuilder.append(ARFFATTRIBUTE + " " + DATEATTRIBUTE + " " + ARFFDATE
				+ lineseparator);
		stringBuilder.append(ARFFDATASECTION );
	}
	/**
	 * this method adds one single {@link Observation} to the current arff string by:
	 * inserting the timestamp of the observation, inserting the observed free
	 * slots (if that is <0 then inserting ?) and finally inserting the values
	 * of the {@link OverlayAttribute}
	 * 
	 * @param arffString
	 *            the current arff string in form of as {@link StringBuilder}
	 * @param parkingObservation
	 *            the {@link Observation} made at the parking place
	 * @param overlayAttrs
	 *            the list of {@link OverlayAttribute} to be included in the arff
	 *            string. This can be null, if the timeseries is univariate
	 * @param config the configuration of the model
	 */
	public void addSingleArffInstance( StringBuilder arffString,
			 Observation parkingObservation,
			 OverlayAttributes overlayAttrs,  TSModelConfig config) {
		if(arffString==null||parkingObservation==null||config==null)
			return;
		String lineseparator = System.getProperty("line.separator");
		int freeSlots = parkingObservation.getObservedValue();
		Timestamp observationTime = parkingObservation.getTimestamp();
		arffString.append(lineseparator);
		if (freeSlots < 0)
			arffString.append("?,");
		else
			arffString.append(freeSlots + ",");
		if (overlayAttrs != null) {
			for (OverlayAttribute ol : overlayAttrs.getOverlayAttributes()) {
				arffString.append(ol.getAttributeValue(observationTime, config.getOverlayStrategy()));
				arffString.append(",");
			}
		}
		arffString.append("\"");
		arffString.append(config.getDateformatInUse()
				.format(parkingObservation.getTimestamp()));
		arffString.append("\"");

	}
	

	

}
