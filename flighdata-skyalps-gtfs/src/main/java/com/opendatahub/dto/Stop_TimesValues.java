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
	private stop_sequence stop_sequence; // this must be a not negative integer. Values must increase along the trip but
	// do not need to be consecutive.
	// Supported values for stop_sequence are: 1 as the departing airport and 2 as
	// the arrival airport. Considering enum type class.
	private String stop_headsign; // this value overrides the default value trip_headsign set in trips.txt, to be
									// used when head-sign changes between stops.
	private pickup_type pickyp_type;
	private pickup_type dropoff_type;
	private continous_pickup_stopTimes continous_pickyp;
	private continous_pickup_stopTimes continous_dropoff;
	private float shape_dist_traveled; // this must be a non negative float.
	private timepoint timepoint;

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

	public stop_sequence getStop_sequence() {
		return stop_sequence;
	}

	public void setStop_sequence(stop_sequence stop_sequence) {
		this.stop_sequence = stop_sequence;
	}

	public String getStop_headsign() {
		return stop_headsign;
	}

	public void setStop_headsign(String stop_headsign) {
		this.stop_headsign = stop_headsign;
	}

	public pickup_type getPickyp_type() {
		return pickyp_type;
	}

	public void setPickyp_type(pickup_type pickyp_type) {
		this.pickyp_type = pickyp_type;
	}

	public pickup_type getDropoff_type() {
		return dropoff_type;
	}

	public void setDropoff_type(pickup_type dropoff_type) {
		this.dropoff_type = dropoff_type;
	}

	public continous_pickup_stopTimes getContinous_pickyp() {
		return continous_pickyp;
	}

	public void setContinous_pickyp(continous_pickup_stopTimes continous_pickyp) {
		this.continous_pickyp = continous_pickyp;
	}

	public continous_pickup_stopTimes getContinous_dropoff() {
		return continous_dropoff;
	}

	public void setContinous_dropoff(continous_pickup_stopTimes continous_dropoff) {
		this.continous_dropoff = continous_dropoff;
	}

	public float getShape_dist_traveled() {
		return shape_dist_traveled;
	}

	public void setShape_dist_traveled(float shape_dist_traveled) {
		this.shape_dist_traveled = shape_dist_traveled;
	}

	public timepoint getTimepoint() {
		return timepoint;
	}

	public void setTimepoint(timepoint timepoint) {
		this.timepoint = timepoint;
	}

	public Stop_TimesValues(String trip_id, String arrival_time, String departure_time, String stop_id,
			stop_sequence stop_sequence, String stop_headsign, pickup_type pickyp_type, pickup_type dropoff_type,
			continous_pickup_stopTimes continous_pickyp, continous_pickup_stopTimes continous_dropoff,
			float shape_dist_traveled, com.opendatahub.enumClasses.timepoint timepoint) {
		super();
		this.trip_id = trip_id;
		this.arrival_time = arrival_time;
		this.departure_time = departure_time;
		this.stop_id = stop_id;
		this.stop_sequence = stop_sequence;
		this.stop_headsign = stop_headsign;
		this.pickyp_type = pickyp_type;
		this.dropoff_type = dropoff_type;
		this.continous_pickyp = continous_pickyp;
		this.continous_dropoff = continous_dropoff;
		this.shape_dist_traveled = shape_dist_traveled;
		this.timepoint = timepoint;
	}

	public Stop_TimesValues(String trip_id, String arrival_time, String departure_time, String stop_id,
			stop_sequence stop_sequence) {
		super();
		this.trip_id = trip_id;
		this.arrival_time = arrival_time;
		this.departure_time = departure_time;
		this.stop_id = stop_id;
		this.stop_sequence = stop_sequence;
	}

	public Stop_TimesValues(String trip_id, String stop_id, stop_sequence stop_sequence) {
		super();
		this.trip_id = trip_id;
		this.stop_id = stop_id;
		this.stop_sequence = stop_sequence;
	}

	@Override
	public String toString() {
		return "Stop_TimesValues [trip_id=" + trip_id + ", arrival_time=" + arrival_time + ", departure_time="
				+ departure_time + ", stop_id=" + stop_id + ", stop_sequence=" + stop_sequence + ", stop_headsign="
				+ stop_headsign + ", pickyp_type=" + pickyp_type + ", dropoff_type=" + dropoff_type
				+ ", continous_pickyp=" + continous_pickyp + ", continous_dropoff=" + continous_dropoff
				+ ", shape_dist_traveled=" + shape_dist_traveled + ", timepoint=" + timepoint + "]";
	}

}
