package com.opendatahub.constantsClasses;

public class Agency {
	private String agency_id = "agency_id";
	private String agencyname = "agency_name";
	private String agency_url = "agency_url";
	private String agency_timezone = "agency_timezone";
	private String agency_lang = "agency_lang";
	private String agency_phone = "agency_phone";
	private String agency_fare_url = "agency_fare_url";
	private String agency_email = "agency_email";

	public String getAgency_id() {
		return agency_id;
	}

	public String getAgencyname() {
		return agencyname;
	}

	public String getAgency_url() {
		return agency_url;
	}

	public String getAgency_timezone() {
		return agency_timezone;
	}

	public String getAgency_lang() {
		return agency_lang;
	}

	public String getAgency_phone() {
		return agency_phone;
	}

	public String getAgency_fare_url() {
		return agency_fare_url;
	}

	public String getAgency_email() {
		return agency_email;
	}

	public void setAgency_id(String agency_id) {
		this.agency_id = agency_id;
	}

	public void setAgencyname(String agencyname) {
		this.agencyname = agencyname;
	}

	public void setAgency_url(String agency_url) {
		this.agency_url = agency_url;
	}

	public void setAgency_timezone(String agency_timezone) {
		this.agency_timezone = agency_timezone;
	}

	public void setAgency_lang(String agency_lang) {
		this.agency_lang = agency_lang;
	}

	public void setAgency_phone(String agency_phone) {
		this.agency_phone = agency_phone;
	}

	public void setAgency_fare_url(String agency_fare_url) {
		this.agency_fare_url = agency_fare_url;
	}

	public void setAgency_email(String agency_email) {
		this.agency_email = agency_email;
	}

	@Override
	public String toString() {
		return "Agency []";
	}

}
