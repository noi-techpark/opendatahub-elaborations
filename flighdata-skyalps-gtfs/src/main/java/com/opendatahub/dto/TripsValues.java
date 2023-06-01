// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.dto;
import java.io.Serializable;
import java.lang.String;
import org.springframework.lang.NonNull;

import com.opendatahub.enumClasses.bikes_allowed;
import com.opendatahub.enumClasses.wheelchair_accessible;
public class TripsValues implements Serializable {

    private static final long serialVersionUID = 1L;
	private String route_id; // read specifications
	@NonNull
	private String service_id;
	@NonNull
	private String trip_id; // scode
	private int direction_id;// Check if the in the ODH API if a flight departs from Bolzano (in this case
								// value is 0) or arrives to Bolzano (int his case value is 1)

	public String getRoute_id() {
		return route_id;
	}

	public void setRoute_id(String route_id) {
		this.route_id = route_id;
	}

	public String getService_id() {
		return service_id;
	}

	public void setService_id(String service_id) {
		this.service_id = service_id;
	}

	public String getTrip_id() {
		return trip_id;
	}

	public void setTrip_id(String trip_id) {
		this.trip_id = trip_id;
	}

	public int getDirection_id() {
		return direction_id;
	}

	public void setDirection_id(int i) {
		this.direction_id = i;
	}

	public TripsValues() {
		// TODO Auto-generated constructor stub
	}

	public TripsValues(String route_id, String service_id, String trip_id, int direction_id) {
		super();
		this.route_id = route_id;
		this.service_id = service_id;
		this.trip_id = trip_id;
		this.direction_id = direction_id;
	}

	@Override
	public String toString() {
		return "TripsValues [route_id=" + route_id + ", service_id=" + service_id + ", trip_id=" + trip_id
				+ ", direction_id=" + direction_id + "]";
	}

}
