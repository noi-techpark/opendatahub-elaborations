// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.overlay.weather;

import java.io.Serializable;

public class IntegreenObservation implements Serializable{
	/**
	 * 
	 */
	private static final long serialVersionUID = 6244279973550897493L;
	private Long timestamp;
	private Double value;
	
	
	
	public Long getTimestamp() {
		return timestamp;
	}
	public void setTimestamp(Long timestamp) {
		this.timestamp = timestamp;
	}
	public Double getValue() {
		return value;
	}
	public void setValue(Double value) {
		this.value = value;
	}
	
	
}
