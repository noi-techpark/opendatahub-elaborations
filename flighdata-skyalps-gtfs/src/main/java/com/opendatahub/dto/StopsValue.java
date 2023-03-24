package com.opendatahub.dto;
import java.io.Serializable;

import java.lang.String;
import java.net.URL;

import javax.validation.Valid;

import org.springframework.lang.NonNull;
import org.springframework.validation.annotation.Validated;

import com.opendatahub.validation.CheckLocationType;
import com.opendatahub.validation.ConditionalValid;
import com.opendatahub.enumClasses.location_type;
import com.opendatahub.enumClasses.parentless_stops;
public class StopsValue implements Serializable {

    private static final long serialVersionUID = 1L;
	@NonNull
	private String stop_id; // To be taken from the field sname of the ODH API
	private String stop_code;
	@NonNull
	private String stop_name;
	private String tts_stop_name;
	private String stop_desc;
	@NonNull
	private Double stop_lat;
	@NonNull
	private Double stop_lon;
	@NonNull
	private String zone_id; // Required if fare_rules.txt is used
	private URL stop_URL;
	private location_type location_type;
	@NonNull
	private Integer parent_station; // Required if location_type is used
	private String stop_timezone;
	private parentless_stops wheelchair_boarding;
	private String level_id;
	private String platform_code;

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

	public String getTts_stop_name() {
		return tts_stop_name;
	}

	public void setTts_stop_name(String tts_stop_name) {
		this.tts_stop_name = tts_stop_name;
	}

	public String getStop_desc() {
		return stop_desc;
	}

	public void setStop_desc(String stop_desc) {
		this.stop_desc = stop_desc;
	}

	public Double getStop_lat() {
		return stop_lat;
	}

	public void setStop_lat(Double stop_lat) {
		this.stop_lat = stop_lat;
	}

	public Double getStop_lon() {
		return stop_lon;
	}

	public void setStop_lon(Double stop_lon) {
		this.stop_lon = stop_lon;
	}

	public String getZone_id() {
		return zone_id;
	}

	public void setZone_id(String zone_id) {
		this.zone_id = zone_id;
	}

	public URL getStop_URL() {
		return stop_URL;
	}

	public void setStop_URL(URL stop_URL) {
		this.stop_URL = stop_URL;
	}

	public location_type getLocation_type() {
		return location_type;
	}

	public void setLocation_type(location_type location_type) {
		this.location_type = location_type;
	}

	public Integer getParent_station() {
		return parent_station;
	}

	public void setParent_station(Integer parent_station) {
		this.parent_station = parent_station;
	}

	public String getStop_timezone() {
		return stop_timezone;
	}

	public void setStop_timezone(String stop_timezone) {
		this.stop_timezone = stop_timezone;
	}

	public parentless_stops getWheelchair_boarding() {
		return wheelchair_boarding;
	}

	public void setWheelchair_boarding(parentless_stops wheelchair_boarding) {
		this.wheelchair_boarding = wheelchair_boarding;
	}

	public String getLevel_id() {
		return level_id;
	}

	public void setLevel_id(String level_id) {
		this.level_id = level_id;
	}

	public String getPlatform_code() {
		return platform_code;
	}

	public void setPlatform_code(String platform_code) {
		this.platform_code = platform_code;
	}

	public StopsValue(String stop_id, String stop_code, String stop_name, String tts_stop_name,
			java.lang.String stop_desc, Double stop_lat, Double stop_lon, java.lang.String zone_id, URL stop_URL,
			com.opendatahub.enumClasses.location_type location_type, Integer parent_station,
			java.lang.String stop_timezone, parentless_stops wheelchair_boarding, java.lang.String level_id,
			java.lang.String platform_code) {
		super();
		this.stop_id = stop_id;
		this.stop_code = stop_code;
		this.stop_name = stop_name;
		this.tts_stop_name = tts_stop_name;
		this.stop_desc = stop_desc;
		this.stop_lat = stop_lat;
		this.stop_lon = stop_lon;
		this.zone_id = zone_id;
		this.stop_URL = stop_URL;
		this.location_type = location_type;
		this.parent_station = parent_station;
		this.stop_timezone = stop_timezone;
		this.wheelchair_boarding = wheelchair_boarding;
		this.level_id = level_id;
		this.platform_code = platform_code;
	}

	public StopsValue(String stop_id, String stop_name, Double stop_lat, Double stop_lon, String zone_id) {
		super();
		this.stop_id = stop_id;
		this.stop_name = stop_name;
		this.stop_lat = stop_lat;
		this.stop_lon = stop_lon;
		this.zone_id = zone_id;
	}

	@Override
	public String toString() {
		return "StopsValue [stop_id=" + stop_id + ", stop_code=" + stop_code + ", stop_name=" + stop_name
				+ ", tts_stop_name=" + tts_stop_name + ", stop_desc=" + stop_desc + ", stop_lat=" + stop_lat
				+ ", stop_lon=" + stop_lon + ", zone_id=" + zone_id + ", stop_URL=" + stop_URL + ", location_type="
				+ location_type + ", parent_station=" + parent_station + ", stop_timezone=" + stop_timezone
				+ ", wheelchair_boarding=" + wheelchair_boarding + ", level_id=" + level_id + ", platform_code="
				+ platform_code + "]";
	}

}
