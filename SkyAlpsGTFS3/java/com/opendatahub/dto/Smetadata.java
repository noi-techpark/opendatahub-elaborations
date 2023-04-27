package com.opendatahub.dto;
import java.lang.String;
import java.io.Serializable;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
@JsonIgnoreProperties(ignoreUnknown = false)
public class Smetadata implements Serializable {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private String sta;
	private String std;
	private String ssim;
	private fares fares;
	private String accode;
	private String airlineid;
	private String fltnumber;
	private boolean weekdayfri;
	private boolean weekdaymon;
	private boolean weekdaysat;
	private boolean weekdaysun;
	private boolean weekdaythu;
	private boolean weekdaytue;
	private boolean weekdaywed;
	private String airlinename;
	private String fltstoperiod;
	private String todestination;
	private String fltsfromperiod;
	private String fromdestination;
	private long arrival_timestamp;
	private long departure_timestamp;

	public Smetadata() {

	}

	public String getSta() {
		return sta;
	}

	public void setSta(String sta) {
		this.sta = sta;
	}

	public String getStd() {
		return std;
	}

	public void setStd(String std) {
		this.std = std;
	}

	public String getSsim() {
		return ssim;
	}

	public void setSsim(String ssim) {
		this.ssim = ssim;
	}

	public fares getFares() {
		return fares;
	}

	public void setFares(fares fares) {
		this.fares = fares;
	}

	public String getAccode() {
		return accode;
	}

	public void setAccode(String accode) {
		this.accode = accode;
	}

	public String getAirlineid() {
		return airlineid;
	}

	public void setAirlineid(String airlineid) {
		this.airlineid = airlineid;
	}

	public String getFltnumber() {
		return fltnumber;
	}

	public void setFltnumber(String fltnumber) {
		this.fltnumber = fltnumber;
	}

	public boolean isWeekdayfri() {
		return weekdayfri;
	}

	public void setWeekdayfri(boolean weekdayfri) {
		this.weekdayfri = weekdayfri;
	}

	public boolean isWeekdaymon() {
		return weekdaymon;
	}

	public void setWeekdaymon(boolean weekdaymon) {
		this.weekdaymon = weekdaymon;
	}

	public boolean isWeekdaysat() {
		return weekdaysat;
	}

	public void setWeekdaysat(boolean weekdaysat) {
		this.weekdaysat = weekdaysat;
	}

	public boolean isWeekdaysun() {
		return weekdaysun;
	}

	public void setWeekdaysun(boolean weekdaysun) {
		this.weekdaysun = weekdaysun;
	}

	public boolean isWeekdaythu() {
		return weekdaythu;
	}

	public void setWeekdaythu(boolean weekdaythu) {
		this.weekdaythu = weekdaythu;
	}

	public boolean isWeekdaytue() {
		return weekdaytue;
	}

	public void setWeekdaytue(boolean weekdaytue) {
		this.weekdaytue = weekdaytue;
	}

	public boolean isWeekdaywed() {
		return weekdaywed;
	}

	public void setWeekdaywed(boolean weekdaywed) {
		this.weekdaywed = weekdaywed;
	}

	public String getAirlinename() {
		return airlinename;
	}

	public void setAirlinename(String airlinename) {
		this.airlinename = airlinename;
	}

	public String getFltstoperiod() {
		return fltstoperiod;
	}

	public void setFltstoperiod(String fltstoperiod) {
		this.fltstoperiod = fltstoperiod;
	}

	public String getTodestination() {
		return todestination;
	}

	public void setTodestination(String todestination) {
		this.todestination = todestination;
	}

	public String getFltsfromperiod() {
		return fltsfromperiod;
	}

	public void setFltsfromperiod(String fltsfromperiod) {
		this.fltsfromperiod = fltsfromperiod;
	}

	public String getFromdestination() {
		return fromdestination;
	}

	public void setFromdestination(String fromdestination) {
		this.fromdestination = fromdestination;
	}

	public long getArrival_timestamp() {
		return arrival_timestamp;
	}

	public void setArrival_timestamp(long arrival_timestamp) {
		this.arrival_timestamp = arrival_timestamp;
	}

	public long getDeparture_timestamp() {
		return departure_timestamp;
	}

	public void setDeparture_timestamp(long departure_timestamp) {
		this.departure_timestamp = departure_timestamp;
	}

	public Smetadata(String sta, String std, String ssim, fares fares, String accode, String airlineid,
			String fltnumber, boolean weekdayfri, boolean weekdaymon, boolean weekdaysat, boolean weekdaysun,
			boolean weekdaythu, boolean weekdaytue, boolean weekdaywed, String airlinename, String fltstoperiod,
			String todestination, String fltsfromperiod, String fromdestination, long arrival_timestamp,
			long departure_timestamp) {
		super();
		this.sta = sta;
		this.std = std;
		this.ssim = ssim;
		this.fares = fares;
		this.accode = accode;
		this.airlineid = airlineid;
		this.fltnumber = fltnumber;
		this.weekdayfri = weekdayfri;
		this.weekdaymon = weekdaymon;
		this.weekdaysat = weekdaysat;
		this.weekdaysun = weekdaysun;
		this.weekdaythu = weekdaythu;
		this.weekdaytue = weekdaytue;
		this.weekdaywed = weekdaywed;
		this.airlinename = airlinename;
		this.fltstoperiod = fltstoperiod;
		this.todestination = todestination;
		this.fltsfromperiod = fltsfromperiod;
		this.fromdestination = fromdestination;
		this.arrival_timestamp = arrival_timestamp;
		this.departure_timestamp = departure_timestamp;
	}

	@Override
	public String toString() {
		return "Smetadata [sta=" + sta + ", std=" + std + ", ssim=" + ssim + ", fares=" + fares + ", accode=" + accode
				+ ", airlineid=" + airlineid + ", fltnumber=" + fltnumber + ", weekdayfri=" + weekdayfri
				+ ", weekdaymon=" + weekdaymon + ", weekdaysat=" + weekdaysat + ", weekdaysun=" + weekdaysun
				+ ", weekdaythu=" + weekdaythu + ", weekdaytue=" + weekdaytue + ", weekdaywed=" + weekdaywed
				+ ", airlinename=" + airlinename + ", fltstoperiod=" + fltstoperiod + ", todestination=" + todestination
				+ ", fltsfromperiod=" + fltsfromperiod + ", fromdestination=" + fromdestination + ", arrival_timestamp="
				+ arrival_timestamp + ", departure_timestamp=" + departure_timestamp + "]";
	}

}
