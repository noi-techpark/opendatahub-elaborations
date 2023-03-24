package com.opendatahub.dto;
import java.net.URL;

import org.springframework.lang.NonNull;

import com.opendatahub.enumClasses.continous_drop_off;
import com.opendatahub.enumClasses.continous_pickup;
import com.opendatahub.enumClasses.route_color;
import com.opendatahub.enumClasses.route_type;

import java.io.Serializable;
import java.lang.String;
public class RoutesValues implements Serializable {

    private static final long serialVersionUID = 1L;
	@NonNull
	private String route_id; // read specification
	@NonNull
	private String agency_id;
	@NonNull
	private String route_short_name;
	@NonNull
	private String route_long_name;
	private String route_desc;
	@NonNull
	private route_type route_type;// default value 1100
	private URL route_URL;
	private route_color route_color;
	private route_color route_text_color;
	private int route_sort_order;
	private continous_pickup continous_pickup; // optional only in case "route" is given by shapes.txt
	private continous_drop_off continous_drop_off; // optional only in case "route" is given by shapes.txt

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

	public route_type getRoute_type() {
		return route_type;
	}

	public void setRoute_type(route_type route_type) {
		this.route_type = route_type;
	}

	public URL getRoute_URL() {
		return route_URL;
	}

	public void setRoute_URL(URL route_URL) {
		this.route_URL = route_URL;
	}

	public route_color getRoute_color() {
		return route_color;
	}

	public void setRoute_color(route_color route_color) {
		this.route_color = route_color;
	}

	public route_color getRoute_text_color() {
		return route_text_color;
	}

	public void setRoute_text_color(route_color route_text_color) {
		this.route_text_color = route_text_color;
	}

	public int getRoute_sort_order() {
		return route_sort_order;
	}

	public void setRoute_sort_order(int route_sort_order) {
		this.route_sort_order = route_sort_order;
	}

	public continous_pickup getContinous_pickup() {
		return continous_pickup;
	}

	public void setContinous_pickup(continous_pickup continous_pickup) {
		this.continous_pickup = continous_pickup;
	}

	public continous_drop_off getContinous_drop_off() {
		return continous_drop_off;
	}

	public void setContinous_drop_off(continous_drop_off continous_drop_off) {
		this.continous_drop_off = continous_drop_off;
	}

	public RoutesValues(String route_id, String agency_id, String route_short_name, String route_long_name,
			String route_desc, com.opendatahub.enumClasses.route_type route_type, URL route_URL,
			com.opendatahub.enumClasses.route_color route_color,
			com.opendatahub.enumClasses.route_color route_text_color, int route_sort_order,
			com.opendatahub.enumClasses.continous_pickup continous_pickup,
			com.opendatahub.enumClasses.continous_drop_off continous_drop_off) {
		super();
		this.route_id = route_id;
		this.agency_id = agency_id;
		this.route_short_name = route_short_name;
		this.route_long_name = route_long_name;
		this.route_desc = route_desc;
		this.route_type = route_type;
		this.route_URL = route_URL;
		this.route_color = route_color;
		this.route_text_color = route_text_color;
		this.route_sort_order = route_sort_order;
		this.continous_pickup = continous_pickup;
		this.continous_drop_off = continous_drop_off;
	}

	public RoutesValues(String route_id, String agency_id, String route_short_name, String route_long_name,
			com.opendatahub.enumClasses.route_type route_type) {
		super();
		this.route_id = route_id;
		this.agency_id = agency_id;
		this.route_short_name = route_short_name;
		this.route_long_name = route_long_name;
		this.route_type = route_type;
	}

	public RoutesValues() {
		// TODO Auto-generated constructor stub
	}

	@Override
	public String toString() {
		return "RoutesValues [route_id=" + route_id + ", agency_id=" + agency_id + ", route_short_name="
				+ route_short_name + ", route_long_name=" + route_long_name + ", route_desc=" + route_desc
				+ ", route_type=" + route_type + ", route_URL=" + route_URL + ", route_color=" + route_color
				+ ", route_text_color=" + route_text_color + ", route_sort_order=" + route_sort_order
				+ ", continous_pickup=" + continous_pickup + ", continous_drop_off=" + continous_drop_off + "]";
	}

}
