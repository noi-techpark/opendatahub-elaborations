package com.opendatahub.constantsClasses;

public class Stop_Times {

	private String trip_id = "trip_id";
	private String arrival_time = "arrival_time";
	private String departure_time = "departure_time";
	private String stop_id = "stop_id";
	private String stop_sequence = "stop_sequence";

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

	public String getStop_sequence() {
		return stop_sequence;
	}

	public void setStop_sequence(String stop_sequence) {
		this.stop_sequence = stop_sequence;
	}

	@Override
	public String toString() {
		return "Stop_Times [trip_id=" + trip_id + ", arrival_time=" + arrival_time + ", departure_time="
				+ departure_time + ", stop_id=" + stop_id + ", stop_sequence=" + stop_sequence + "]";
	}

	
}
