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
	private String agency_name;
	@NonNull
	private URL agency_url;
	@NonNull
	private agency_timezone agency_timezone;

	public AgencyValues() {

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


	public AgencyValues(String agency_name, URL agency_url,
			com.opendatahub.enumClasses.agency_timezone agency_timezone) {
		super();
		this.agency_name = agency_name;
		this.agency_url = agency_url;
		this.agency_timezone = agency_timezone;
	}

	@Override
	public String toString() {
		return "AgencyValues [agency_name=" + agency_name + ", agency_url=" + agency_url + ", agency_timezone="
				+ agency_timezone + "]";
	}

}
