// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsforecast.domain;

import it.unibz.tsforecast.entity.ParkingPlace;

import com.thoughtworks.xstream.annotations.XStreamAlias;

/**
 * @author mreinstadler This class represents one single forecast for one
 *         parkingplace
 * 
 */
@XStreamAlias("parking-prediction")
public class ParkingPrediction {
	@XStreamAlias("parking-place")
	private ParkingPlace parkingPlace = null;
	@XStreamAlias("slot-prediction")
	private TSPrediction prediction = null;

	

	/**
	 * @param parkingPlace
	 *            the {@link ParkingPlace} where the prediction is fone
	 * @param prediction
	 *            the {@link Prediction} for the parking place
	 */
	public ParkingPrediction(ParkingPlace parkingPlace, TSPrediction prediction) {
		this.parkingPlace = parkingPlace;
		this.prediction = prediction;
	}

	/**
	 * @return the {@link ParkingPlace}
	 */
	public ParkingPlace getParkingPlace() {
		return parkingPlace;
	}

	/**
	 * @return the {@link TSPrediction} of free slots 
	 */
	public TSPrediction getPrediction() {
		return prediction;
	}
	
	

}
