// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.dto;
import java.io.Serializable;
import java.lang.String;
import org.springframework.lang.NonNull;

import com.opendatahub.enumClasses.continous_pickup_stopTimes;
import com.opendatahub.enumClasses.pickup_type;
import com.opendatahub.enumClasses.stop_sequence;
import com.opendatahub.enumClasses.timepoint;
public class Stop_TimesValues implements Serializable {

    private static final long serialVersionUID = 1L;
	@NonNull
	private String trip_id; // trips.txt id
	@NonNull
	private String arrival_time; // smetadata -> sta
	@NonNull
	private String departure_time; // smetadata-> std
	@NonNull
	private String stop_id; // stops.txt id
	@NonNull
	private int stop_sequence; // this must be a not negative integer. Values must increase along the trip but
	// do not need to be consecutive.
	// Supported values for stop_sequence are: 1 as the departing airport and 2 as
	// the arrival airport. Considering enum type class.

	public Stop_TimesValues() {

	}

	public String getTrip_id() {
		return trip_id;
	}

	public void setTrip_id(String trip_id) {
		this.trip_id = trip_id;
	}

	public String getArrival_time() {
		return arrival_time;
	}

	public void setArrival_time(String arrival_time) {
		this.arrival_time = arrival_time;
	}

	public String getDeparture_time() {
		return departure_time;
	}

	public void setDeparture_time(String departure_time) {
		this.departure_time = departure_time;
	}

	public String getStop_id() {
		return stop_id;
	}

	public void setStop_id(String stop_id) {
		this.stop_id = stop_id;
	}

	public int getStop_sequence() {
		return stop_sequence;
	}

	public void setStop_sequence(int i) {
		this.stop_sequence = i;
	}

	public Stop_TimesValues(String trip_id, String arrival_time, String departure_time, String stop_id,
			int stop_sequence) {
		super();
		this.trip_id = trip_id;
		this.arrival_time = arrival_time;
		this.departure_time = departure_time;
		this.stop_id = stop_id;
		this.stop_sequence = stop_sequence;
	}

	@Override
	public String toString() {
		return "Stop_TimesValues [trip_id=" + trip_id + ", arrival_time=" + arrival_time + ", departure_time="
				+ departure_time + ", stop_id=" + stop_id + ", stop_sequence=" + stop_sequence + "]";
	}

	
}
