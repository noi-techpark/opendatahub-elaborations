package com.opendatahub.constantsClasses;

public class Routes {

	private String route_id = "route_id";
	private String agency_id = "agency_id";
	private String route_short_name = "route_short_name";
	private String route_long_name = "route_long_name";
	private String route_desc = "route_desc";
	private String route_type = "route_type";
	private String route_URL = "route_URL";
	private String route_colour = "route_colour";
	private String route_text_color = "route_text_color";
	private String route_sort_order = "route_sort_order";
	private String continous_pickup = "continous_pickup";
	private String continous_drop_off = "continous_drop_off";

	public String getRoute_id() {
		return route_id;
	}

	public void setRoute_id(String route_id) {
		this.route_id = route_id;
	}

	public String getAgency_id() {
		return agency_id;
	}

	public void setAgency_id(String agency_id) {
		this.agency_id = agency_id;
	}

	public String getRoute_short_name() {
		return route_short_name;
	}

	public void setRoute_short_name(String route_short_name) {
		this.route_short_name = route_short_name;
	}

	public String getRoute_long_name() {
		return route_long_name;
	}

	public void setRoute_long_name(String route_long_name) {
		this.route_long_name = route_long_name;
	}

	public String getRoute_desc() {
		return route_desc;
	}

	public void setRoute_desc(String route_desc) {
		this.route_desc = route_desc;
	}

	public String getRoute_type() {
		return route_type;
	}

	public void setRoute_type(String route_type) {
		this.route_type = route_type;
	}

	public String getRoute_URL() {
		return route_URL;
	}

	public void setRoute_URL(String route_URL) {
		this.route_URL = route_URL;
	}

	public String getRoute_colour() {
		return route_colour;
	}

	public void setRoute_colour(String route_colour) {
		this.route_colour = route_colour;
	}

	public String getRoute_text_color() {
		return route_text_color;
	}

	public void setRoute_text_color(String route_text_color) {
		this.route_text_color = route_text_color;
	}

	public String getRoute_sort_order() {
		return route_sort_order;
	}

	public void setRoute_sort_order(String route_sort_order) {
		this.route_sort_order = route_sort_order;
	}

	public String getContinous_pickup() {
		return continous_pickup;
	}

	public void setContinous_pickup(String continous_pickup) {
		this.continous_pickup = continous_pickup;
	}

	public String getContinous_drop_off() {
		return continous_drop_off;
	}

	public void setContinous_drop_off(String continous_drop_off) {
		this.continous_drop_off = continous_drop_off;
	}

	@Override
	public String toString() {
		return "Routes [route_id=" + route_id + ", agency_id=" + agency_id + ", route_short_name=" + route_short_name
				+ ", route_long_name=" + route_long_name + ", route_desc=" + route_desc + ", route_type=" + route_type
				+ ", route_URL=" + route_URL + ", route_colour=" + route_colour + ", route_text_color="
				+ route_text_color + ", route_sort_order=" + route_sort_order + ", continous_pickup=" + continous_pickup
				+ ", continous_drop_off=" + continous_drop_off + "]";
	}

}
