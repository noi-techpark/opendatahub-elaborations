// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.overlay;

import it.unibz.tsmodel.domain.ObservationMetaInfo;

import java.sql.Timestamp;

/**
 * @author mreinstadler This interface must be implemented by each overlay
 * attribute. Weka requires for an overlay attribute a name, a type and a value, which 
 * can be also ? if no value is available
 * 
 */
public interface OverlayAttribute {

	/**
	 * @return the name of the overlay attribute used in the arff header
	 */
	public String getAttributeName();

	/**
	 * @return the format of the overlay attribute used in the arff header
	 */
	public String getAttributeFormat();

	/**
	 * @param timestamp the timestamp of the required observation
	 * @param strategy the strategy used to calculate overlay values
	 * - either boolean values or real values
	 * @return the value of the overlay attribute. It can be numeric (if the 
	 * type is numeric), nominal(if the type is nominal),... and finally ?
	 * if the value is not available
	 */
	public String getAttributeValue(Timestamp timestamp, OverlayStrategy strategy);

	/**
	 * @param timestamp
	 *            the required date in milliseconds for the meta information
	 * @return the eventual meta information about the overlay attribute e.g.
	 *         the weather meta information in the meteo overlay attribute
	 */
	public ObservationMetaInfo getMetaInformation(Timestamp timestamp);
	
	

}
