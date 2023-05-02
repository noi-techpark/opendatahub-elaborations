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
	private int monday;
	@NonNull
	private int tuesday;
	@NonNull
	private int wednesday;
	@NonNull
	private int thursday;
	@NonNull
	private int friday;
	@NonNull
	private int saturday;
	@NonNull
	private int sunday;
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

	public int getMonday() {
		return monday;
	}

	public void setMonday(int monday) {
		this.monday = monday;
	}

	public int getTuesday() {
		return tuesday;
	}

	public void setTuesday(int tuesday) {
		this.tuesday = tuesday;
	}

	public int getWednesday() {
		return wednesday;
	}

	public void setWednesday(int i) {
		this.wednesday = i;
	}

	public int getThursday() {
		return thursday;
	}

	public void setThursday(int thursday) {
		this.thursday = thursday;
	}

	public int getFriday() {
		return friday;
	}

	public void setFriday(int friday) {
		this.friday = friday;
	}

	public int getSaturday() {
		return saturday;
	}

	public void setSaturday(int saturday) {
		this.saturday = saturday;
	}
	
	public int getSunday() {
		return sunday;
	}

	public void setSunday(int sunday) {
		this.sunday = sunday;
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

	public CalendarValues(String service_id, int monday, int tuesday,
			int wednesday, int thursday, int friday,
			int saturday, int sunday, String start_date, String end_date) {
		super();
		this.service_id = service_id;
		this.monday = monday;
		this.tuesday = tuesday;
		this.wednesday = wednesday;
		this.thursday = thursday;
		this.friday = friday;
		this.saturday = saturday;
		this.sunday = sunday;
		this.start_date = start_date;
		this.end_date = end_date;
	}

	@Override
	public String toString() {
		return "CalendarValues [service_id=" + service_id + ", monday=" + monday + ", tuesday=" + tuesday
				+ ", wednesday=" + wednesday + ", thursday=" + thursday + ", friday=" + friday + ", saturday="
				+ saturday + ", sunday="+ sunday + ", start_date=" + start_date + ", end_date=" + end_date + "]";
	}

}
