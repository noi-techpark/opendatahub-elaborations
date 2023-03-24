package com.opendatahub.constantsClasses;

public class Trips {

	private String route_id = "route_id";
	private String service_id = "service_id";
	private String trip_id = "trip_id";
	private String trip_headsign = "trip_headsign";
	private String trip_short_name = "trip_short_name";
	private String direction_id = "direction_id";
	private String block_id = "block_id";
	private String shape_id = "shape_id";
	private String wheelchair_accessible = "wheelchair_accessible";
	private String bikes_allowed = "bikes_allowed";

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

	public String getTrip_headsign() {
		return trip_headsign;
	}

	public void setTrip_headsign(String trip_headsign) {
		this.trip_headsign = trip_headsign;
	}

	public String getTrip_short_name() {
		return trip_short_name;
	}

	public void setTrip_short_name(String trip_short_name) {
		this.trip_short_name = trip_short_name;
	}

	public String getDirection_id() {
		return direction_id;
	}

	public void setDirection_id(String direction_id) {
		this.direction_id = direction_id;
	}

	public String getBlock_id() {
		return block_id;
	}

	public void setBlock_id(String block_id) {
		this.block_id = block_id;
	}

	public String getShape_id() {
		return shape_id;
	}

	public void setShape_id(String shape_id) {
		this.shape_id = shape_id;
	}

	public String getWheelchair_accessible() {
		return wheelchair_accessible;
	}

	public void setWheelchair_accessible(String wheelchair_accessible) {
		this.wheelchair_accessible = wheelchair_accessible;
	}

	public String getBikes_allowed() {
		return bikes_allowed;
	}

	public void setBikes_allowed(String bikes_allowed) {
		this.bikes_allowed = bikes_allowed;
	}

	@Override
	public String toString() {
		return "Trips [route_id=" + route_id + ", service_id=" + service_id + ", trip_id=" + trip_id
				+ ", trip_headsign=" + trip_headsign + ", trip_short_name=" + trip_short_name + ", direction_id="
				+ direction_id + ", block_id=" + block_id + ", shape_id=" + shape_id + ", wheelchair_accessible="
				+ wheelchair_accessible + ", bikes_allowed=" + bikes_allowed + "]";
	}

}
