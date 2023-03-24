package com.opendatahub.dto;
import java.io.Serializable;
import java.lang.String;
import org.springframework.lang.NonNull;

import com.opendatahub.enumClasses.service_operation;
public class CalendarValues implements Serializable {
    private static final long serialVersionUID = 1L;
	@NonNull
	private String service_id; // to be taken from scode
	@NonNull
	private service_operation monday;
	@NonNull
	private service_operation tuesday;
	@NonNull
	private service_operation wednesday;
	@NonNull
	private service_operation thursday;
	@NonNull
	private service_operation friday;
	@NonNull
	private service_operation saturday;
	@NonNull
	private String start_date; // SimpleDateFormat format = new SimpleDateFormat("yyyyMMdd");
	@NonNull
	private String end_date; // SimpleDateFormat format = new SimpleDateFormat("yyyyMMdd");

	public CalendarValues() {

	}

	public String getService_id() {
		return service_id;
	}

	public void setService_id(String service_id) {
		this.service_id = service_id;
	}

	public service_operation getMonday() {
		return monday;
	}

	public void setMonday(service_operation monday) {
		this.monday = monday;
	}

	public service_operation getTuesday() {
		return tuesday;
	}

	public void setTuesday(service_operation tuesday) {
		this.tuesday = tuesday;
	}

	public service_operation getWednesday() {
		return wednesday;
	}

	public void setWednesday(service_operation wednesday) {
		this.wednesday = wednesday;
	}

	public service_operation getThursday() {
		return thursday;
	}

	public void setThursday(service_operation thursday) {
		this.thursday = thursday;
	}

	public service_operation getFriday() {
		return friday;
	}

	public void setFriday(service_operation friday) {
		this.friday = friday;
	}

	public service_operation getSaturday() {
		return saturday;
	}

	public void setSaturday(service_operation saturday) {
		this.saturday = saturday;
	}

	public String getStart_date() {
		return start_date;
	}

	public void setStart_date(String start_date) {
		this.start_date = start_date;
	}

	public String getEnd_date() {
		return end_date;
	}

	public void setEnd_date(String end_date) {
		this.end_date = end_date;
	}

	public CalendarValues(String service_id, service_operation monday, service_operation tuesday,
			service_operation wednesday, service_operation thursday, service_operation friday,
			service_operation saturday, String start_date, String end_date) {
		super();
		this.service_id = service_id;
		this.monday = monday;
		this.tuesday = tuesday;
		this.wednesday = wednesday;
		this.thursday = thursday;
		this.friday = friday;
		this.saturday = saturday;
		this.start_date = start_date;
		this.end_date = end_date;
	}

	@Override
	public String toString() {
		return "CalendarValues [service_id=" + service_id + ", monday=" + monday + ", tuesday=" + tuesday
				+ ", wednesday=" + wednesday + ", thursday=" + thursday + ", friday=" + friday + ", saturday="
				+ saturday + ", start_date=" + start_date + ", end_date=" + end_date + "]";
	}

}
