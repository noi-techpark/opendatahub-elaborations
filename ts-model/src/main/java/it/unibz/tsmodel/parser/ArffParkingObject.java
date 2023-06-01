// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.parser;

import it.unibz.tsmodel.domain.ParkingPlace;
import it.unibz.tsmodel.overlay.OverlayAttribute;
import it.unibz.tsmodel.overlay.OverlayAttributes;

/**
 * @author mreinstadler this class represents one single arff object, whitch contains
 *         the a string in arff format, a list of {@link OverlayAttribute} and the
 *         {@link ParkingPlace} object the arff string has been build on
 */
public class ArffParkingObject {

	private String arffString;
	private OverlayAttributes overlay = null;
	private ParkingPlace parkingplace = null;
	

	

	/**
	 * @param arffString
	 *            the string in arff format
	 * @param overlayAttrs
	 *            the list of {@link OverlayAttribute}
	 * @param parkingPlace
	 *            the {@link ParkingPlace} object
	 */
	public ArffParkingObject(String arffString, OverlayAttributes overlayAttrs,
			ParkingPlace parkingPlace) {
		this.arffString = arffString;
		this.overlay = overlayAttrs;
		this.parkingplace = parkingPlace;
	}

	/**
	 * @return the string in arff format
	 */
	public String getArffString() {
		return arffString;
	}

	/**
	 * @param arffString
	 *            the string in arff format
	 */
	public void setArffString(String arffString) {
		this.arffString = arffString;
	}

	/**
	 * @return the list of {@link OverlayAttribute} used to build
	 * the arff string
	 */
	public OverlayAttributes getOverlay() {
		return overlay;
	}

	/**
	 * @param overlay
	 *            the list of {@link OverlayAttribute} used to build
	 *            the arff string
	 */
	public void setOverlay(OverlayAttributes overlay) {
		this.overlay = overlay;
	}

	
	/**
	 * @return the {@link ParkingPlace} object on which the arff 
	 * string has been build
	 */
	public ParkingPlace getParkingplace() {
		return parkingplace;
	}

	/**
	 * @param parkingplace
	 *            the {@link ParkingPlace} on which the arff 
	 *            string should be build on
	 */
	public void setParkingplace(ParkingPlace parkingplace) {
		this.parkingplace = parkingplace;
	}
	

}
