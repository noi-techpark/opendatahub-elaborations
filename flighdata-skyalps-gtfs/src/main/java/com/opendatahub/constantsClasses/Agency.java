// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.constantsClasses;

public class Agency {
	private String agencyname = "agency_name";
	private String agency_url = "agency_url";
	private String agency_timezone = "agency_timezone";


	public String getAgencyname() {
		return agencyname;
	}

	public String getAgency_url() {
		return agency_url;
	}

	public String getAgency_timezone() {
		return agency_timezone;
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

	@Override
	public String toString() {
		return "Agency [agencyname=" + agencyname + ", agency_url=" + agency_url + ", agency_timezone="
				+ agency_timezone + "]";
	}


}
