package com.opendatahub.dto;
import java.io.Serializable;

import java.lang.String;
import java.net.URL;

import javax.validation.Valid;

import org.springframework.lang.NonNull;
import org.springframework.validation.annotation.Validated;

import com.opendatahub.Validation.CheckLocationType;
import com.opendatahub.Validation.ConditionalValid;
import com.opendatahub.enumClasses.location_type;
import com.opendatahub.enumClasses.parentless_stops;
public class StopsValue implements Serializable {

    private static final long serialVersionUID = 1L;
	@NonNull
	private String stop_id; // To be taken from the field sname of the ODH API
	private String stop_code;
	@NonNull
	private String stop_name;
	@NonNull
	private String stop_lat;
	@NonNull
	private String stop_lon;

	public StopsValue() {

	}

	public String getStop_id() {
		return stop_id;
	}

	public void setStop_id(String stop_id) {
		this.stop_id = stop_id;
	}

	public String getStop_code() {
		return stop_code;
	}

	public void setStop_code(String stop_code) {
		this.stop_code = stop_code;
	}
	@NonNull
	public String getStop_name() {
		return stop_name;
	}
	@NonNull
	public void setStop_name(String stop_name) {
		this.stop_name = stop_name;
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

	public StopsValue(String stop_id, String stop_code, String stop_name, String stop_lat, String stop_lon) {
		super();
		this.stop_id = stop_id;
		this.stop_code = stop_code;
		this.stop_name = stop_name;
		this.stop_lat = stop_lat;
		this.stop_lon = stop_lon;
	}

	@Override
	public String toString() {
		return "StopsValue [stop_id=" + stop_id + ", stop_code=" + stop_code + ", stop_name=" + stop_name
				+ ", stop_lat=" + stop_lat + ", stop_lon=" + stop_lon + "]";
	}


}
