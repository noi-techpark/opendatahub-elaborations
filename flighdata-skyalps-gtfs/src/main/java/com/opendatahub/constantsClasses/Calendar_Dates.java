package com.opendatahub.constantsClasses;

public class Calendar_Dates {

	private String service_id = "service_id";
	private String date = "date";
	private String exception_type = "exception_type";

	public String getService_id() {
		return service_id;
	}

	public void setService_id(String service_id) {
		this.service_id = service_id;
	}

	public String getDate() {
		return date;
	}

	public void setDate(String date) {
		this.date = date;
	}

	public String getException_type() {
		return exception_type;
	}

	public void setException_type(String exception_type) {
		this.exception_type = exception_type;
	}

	public void setException_type(int exception_type) {
		this.exception_type = String.valueOf(exception_type);
	}

	@Override
	public String toString() {
		return "Calendar_Dates [service_id=" + service_id + ", date=" + date + ", exception_type=" + exception_type
				+ "]";
	}

}
