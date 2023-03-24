package com.opendatahub.constantsClasses;

public class Stops {

	private String stopdi = "stop_id";
	private String stopcode = "stop_code";
	private String stopname = "stop_name";
	private String tt_stop_name = "tts_stop_name";
	private String stop_desc = "stop_desc";
	private String stop_lat = "stop_lat";
	private String stop_lon = "stop_lon";
	private String zone_id = "zone_id";
	private String stop_URL = "stop_URL";
	private String location_type = "location_type";
	private String parent_station = "parent_station";
	private String stop_timezone = "stop_timezone";
	private String wheelchair_boarding = "wheelchair_boarding";
	private String level_id = "level_id";
	private String platform_code = "platform_code";

	public String getStopdi() {
		return stopdi;
	}

	public void setStopdi(String stopdi) {
		this.stopdi = stopdi;
	}

	public String getStopcode() {
		return stopcode;
	}

	public void setStopcode(String stopcode) {
		this.stopcode = stopcode;
	}

	public String getStopname() {
		return stopname;
	}

	public void setStopname(String stopname) {
		this.stopname = stopname;
	}

	public String getTt_stop_name() {
		return tt_stop_name;
	}

	public void setTt_stop_name(String tt_stop_name) {
		this.tt_stop_name = tt_stop_name;
	}

	public String getStop_desc() {
		return stop_desc;
	}

	public void setStop_desc(String stop_desc) {
		this.stop_desc = stop_desc;
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

	public String getZone_id() {
		return zone_id;
	}

	public void setZone_id(String zone_id) {
		this.zone_id = zone_id;
	}

	public String getStop_URL() {
		return stop_URL;
	}

	public void setStop_URL(String stop_URL) {
		this.stop_URL = stop_URL;
	}

	public String getLocation_type() {
		return location_type;
	}

	public void setLocation_type(String location_type) {
		this.location_type = location_type;
	}

	public String getParent_station() {
		return parent_station;
	}

	public void setParent_station(String parent_station) {
		this.parent_station = parent_station;
	}

	public String getStop_timezone() {
		return stop_timezone;
	}

	public void setStop_timezone(String stop_timezone) {
		this.stop_timezone = stop_timezone;
	}

	public String getWheelchair_boarding() {
		return wheelchair_boarding;
	}

	public void setWheelchair_boarding(String wheelchair_boarding) {
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

	@Override
	public String toString() {
		return "Stops [stopdi=" + stopdi + ", stopcode=" + stopcode + ", stopname=" + stopname + ", tt_stop_name="
				+ tt_stop_name + ", stop_desc=" + stop_desc + ", stop_lat=" + stop_lat + ", stop_lon=" + stop_lon
				+ ", zone_id=" + zone_id + ", stop_URL=" + stop_URL + ", location_type=" + location_type
				+ ", parent_station=" + parent_station + ", stop_timezone=" + stop_timezone + ", wheelchair_boarding="
				+ wheelchair_boarding + ", level_id=" + level_id + ", platform_code=" + platform_code + "]";
	}

}
