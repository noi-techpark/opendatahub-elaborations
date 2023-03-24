package com.opendatahub.dto;
import java.io.Serializable;
import java.lang.String;
import java.net.URL;

import org.springframework.lang.NonNull;

import com.opendatahub.enumClasses.agency_lang;
import com.opendatahub.enumClasses.agency_timezone;
public class AgencyValues implements Serializable {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	@NonNull
	private String agency_id;
	private String agency_name;
	@NonNull
	private URL agency_url;
	@NonNull
	private agency_timezone agency_timezone;
	private agency_lang agency_lang;
	private String agency_phone;
	private URL agency_fare_url;
	private String agency_email;

	public AgencyValues() {

	}

	public String getAgency_id() {
		return agency_id;
	}

	public String setAgency_id(String agency_id) {
		return this.agency_id = agency_id;
	}

	public String getAgency_name() {
		return agency_name;
	}

	public String setAgency_name(String agency_name) {
		return this.agency_name = agency_name;
	}

	public URL getAgency_url() {
		return agency_url;
	}

	public URL setAgency_url(URL agency_url) {
		return this.agency_url = agency_url;
	}

	public agency_timezone getAgency_timezone() {
		return agency_timezone;
	}

	public agency_timezone setAgency_timezone(agency_timezone agency_timezone) {
		return this.agency_timezone = agency_timezone;
	}

	public agency_lang getAgency_lang() {
		return agency_lang;
	}

	public agency_lang setAgency_lang(agency_lang agency_lang) {
		return this.agency_lang = agency_lang;
	}

	public String getAgency_phone() {
		return agency_phone;
	}

	public String setAgency_phone(String agency_phone) {
		return this.agency_phone = agency_phone;
	}

	public URL getAgency_fare_url() {
		return agency_fare_url;
	}

	public URL setAgency_fare_url(URL agency_fare_url) {
		return this.agency_fare_url = agency_fare_url;
	}

	public String getAgency_email() {
		return agency_email;
	}

	public String setAgency_email(String agency_email) {
		return this.agency_email = agency_email;
	}

	public AgencyValues(String agency_id, String agency_name, URL agency_url,
			com.opendatahub.enumClasses.agency_timezone agency_timezone,
			com.opendatahub.enumClasses.agency_lang agency_lang, String agency_phone, URL agency_fare_url,
			String agency_email) {
		super();
		this.agency_id = agency_id;
		this.agency_name = agency_name;
		this.agency_url = agency_url;
		this.agency_timezone = agency_timezone;
		this.agency_lang = agency_lang;
		this.agency_phone = agency_phone;
		this.agency_fare_url = agency_fare_url;
		this.agency_email = agency_email;
	}

	public AgencyValues(String agency_name, URL agency_url,
			com.opendatahub.enumClasses.agency_timezone agency_timezone) {
		super();
		this.agency_name = agency_name;
		this.agency_url = agency_url;
		this.agency_timezone = agency_timezone;
	}

	@Override
	public String toString() {
		return "AgencyValues [agency_id=" + agency_id + ", agency_name=" + agency_name + ", agency_url=" + agency_url
				+ ", agency_timezone=" + agency_timezone + ", agency_lang=" + agency_lang + ", agency_phone="
				+ agency_phone + ", agency_fare_url=" + agency_fare_url + ", agency_email=" + agency_email + "]";
	}

}
