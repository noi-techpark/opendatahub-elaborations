package it.noitechpark.constantsClasses;

public class Stop_Times {

	private String trip_id = "trip_id";
	private String arrival_time = "arrival_time";
	private String departure_time = "departure_time";
	private String stop_id = "stop_id";
	private String stop_sequence = "stop_sequence";
	private String stop_headsign = "stop_headsign";
	private String pickup_type = "pickup_type";
	private String dropoff_type = "dropoff_type";
	private String continous_pickup = "continous_pickup";
	private String continous_dropoff = "continous_dropoff";
	private String shape_dist_traveled = "shape_dist_traveled";
	private String timepoint = "timepoint";

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

	public String getStop_headsign() {
		return stop_headsign;
	}

	public void setStop_headsign(String stop_headsign) {
		this.stop_headsign = stop_headsign;
	}

	public String getPickup_type() {
		return pickup_type;
	}

	public void setPickyp_type(String pickyp_type) {
		this.pickup_type = pickyp_type;
	}

	public String getDropoff_type() {
		return dropoff_type;
	}

	public void setDropoff_type(String dropoff_type) {
		this.dropoff_type = dropoff_type;
	}

	public String getContinous_pickup() {
		return continous_pickup;
	}

	public void setContinous_pickup(String continous_pickup) {
		this.continous_pickup = continous_pickup;
	}

	public String getContinous_dropoff() {
		return continous_dropoff;
	}

	public void setContinous_dropoff(String continous_dropoff) {
		this.continous_dropoff = continous_dropoff;
	}

	public String getShape_dist_traveled() {
		return shape_dist_traveled;
	}

	public void setShape_dist_traveled(String shape_dist_traveled) {
		this.shape_dist_traveled = shape_dist_traveled;
	}

	public String getTimepoint() {
		return timepoint;
	}

	public void setTimepoint(String timepoint) {
		this.timepoint = timepoint;
	}

	@Override
	public String toString() {
		return "Stop_Times [trip_id=" + trip_id + ", arrival_time=" + arrival_time + ", departure_time="
				+ departure_time + ", stop_id=" + stop_id + ", stop_sequence=" + stop_sequence + ", stop_headsign="
				+ stop_headsign + ", pickyp_type=" + pickup_type + ", dropoff_type=" + dropoff_type
				+ ", continous_pickup=" + continous_pickup + ", continous_dropoff=" + continous_dropoff
				+ ", shape_dist_traveled=" + shape_dist_traveled + ", timepoint=" + timepoint + "]";
	}

}
