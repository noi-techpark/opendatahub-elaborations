// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.dto;
import java.io.Serializable;
import java.lang.String;
import java.text.SimpleDateFormat;

import org.springframework.lang.NonNull;

import com.opendatahub.enumClasses.exception_type;
public class Calendar_DatesValues implements Serializable {

    private static final long serialVersionUID = 1L;
	@NonNull
	private String service_id; // reference to service_id given in calendar.txt. To be left empty.
	@NonNull
	private SimpleDateFormat date; // date when service exception occurs. To be left empty.
	@NonNull
	private exception_type exception_type; // To be left empty.

	public String getService_id() {
		return service_id;
	}

	public void setService_id(String service_id) {
		this.service_id = service_id;
	}

	public SimpleDateFormat getDate() {
		return date;
	}

	public void setDate(SimpleDateFormat date) {
		this.date = date;
	}

	public exception_type getException_type() {
		return exception_type;
	}

	public void setException_type(exception_type exception_type) {
		this.exception_type = exception_type;
	}

	public Calendar_DatesValues(String service_id, SimpleDateFormat date,
			com.opendatahub.enumClasses.exception_type exception_type) {
		super();
		this.service_id = service_id;
		this.date = date;
		this.exception_type = exception_type;
	}

	public Calendar_DatesValues() {
		// TODO Auto-generated constructor stub
	}

	@Override
	public String toString() {
		return "Calendar_DatesValues [service_id=" + service_id + ", date=" + date + ", exception_type="
				+ exception_type + "]";
	}

}
