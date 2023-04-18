package com.opendatahub.constantsClasses;

public class Trips {

	private String route_id = "route_id";
	private String service_id = "service_id";
	private String trip_id = "trip_id";
	private String direction_id = "direction_id";

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

	public String getDirection_id() {
		return direction_id;
	}

	public void setDirection_id(String direction_id) {
		this.direction_id = direction_id;
	}

	@Override
	public String toString() {
		return "Trips [route_id=" + route_id + ", service_id=" + service_id + ", trip_id=" + trip_id + ", direction_id="
				+ direction_id + "]";
	}

}
