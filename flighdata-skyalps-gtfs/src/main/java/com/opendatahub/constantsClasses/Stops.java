// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.constantsClasses;

public class Stops {

	private String stopdi = "stop_id";
	private String stopcode = "stop_code";
	private String stopname = "stop_name";
	private String stop_lat = "stop_lat";
	private String stop_lon = "stop_lon";

	public String getStopdi() {
		return stopdi;
	}

	public void setStopdi(String stopdi) {
		this.stopdi = stopdi;
	}

	public String getStopcode() {
		return stopcode;
	}

	public void setStopcode(String stopcode) {
		this.stopcode = stopcode;
	}

	public String getStopname() {
		return stopname;
	}

	public void setStopname(String stopname) {
		this.stopname = stopname;
	}

	public String getStop_lat() {
		return stop_lat;
	}

	public void setStop_lat(String stop_lat) {
		this.stop_lat = stop_lat;
	}

	public String getStop_lon() {
		return stop_lon;
	}

	public void setStop_lon(String stop_lon) {
		this.stop_lon = stop_lon;
	}

	@Override
	public String toString() {
		return "Stops [stopdi=" + stopdi + ", stopcode=" + stopcode + ", stopname=" + stopname + ", stop_lat="
				+ stop_lat + ", stop_lon=" + stop_lon + "]";
	}

}
