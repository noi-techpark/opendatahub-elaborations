package com.opendatahub.dto;
import java.io.Serializable;
import java.lang.String;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
@JsonIgnoreProperties(ignoreUnknown = false)
public class fare implements Serializable {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private String type;
	private int count;
	private double tax10W;
	private double tax1RT;
	private double tax20W;
	private double tax2RT;
	private double tax30W;
	private double tax3RT;
	private double tax40W;
	private double tax40RT;
	private String toCode;
	private String toDate;
	private String classes;
	private String fromCode;
	private String fromDate;
	private double adultFareOW;
	private double adultFareRT;
	private String airlinename;
	private double childFareOW;
	private double childFareRT;
	private double infantFareOW;
	private double infantFareRT;
	private String notification;
	private String airlineICAOcode;
	private String airlineDesignator;
	private String chargeTaxOnReturnTrip;

	public fare() {

	}

	public String getType() {
		return type;
	}

	public void setType(String type) {
		this.type = type;
	}

	public int getCount() {
		return count;
	}

	public void setCount(int count) {
		this.count = count;
	}

	public double getTax10W() {
		return tax10W;
	}

	public void setTax10W(double tax10w) {
		tax10W = tax10w;
	}

	public double getTax1RT() {
		return tax1RT;
	}

	public void setTax1RT(double tax1rt) {
		tax1RT = tax1rt;
	}

	public double getTax20W() {
		return tax20W;
	}

	public void setTax20W(double tax20w) {
		tax20W = tax20w;
	}

	public double getTax2RT() {
		return tax2RT;
	}

	public void setTax2RT(double tax2rt) {
		tax2RT = tax2rt;
	}

	public double getTax30W() {
		return tax30W;
	}

	public void setTax30W(double tax30w) {
		tax30W = tax30w;
	}

	public double getTax3RT() {
		return tax3RT;
	}

	public void setTax3RT(double tax3rt) {
		tax3RT = tax3rt;
	}

	public double getTax40W() {
		return tax40W;
	}

	public void setTax40W(double tax40w) {
		tax40W = tax40w;
	}

	public double getTax40RT() {
		return tax40RT;
	}

	public void setTax40RT(double tax40rt) {
		tax40RT = tax40rt;
	}

	public String getToCode() {
		return toCode;
	}

	public void setToCode(String toCode) {
		this.toCode = toCode;
	}

	public String getToDate() {
		return toDate;
	}

	public void setToDate(String toDate) {
		this.toDate = toDate;
	}

	public String getClasses() {
		return classes;
	}

	public void setClasses(String classes) {
		this.classes = classes;
	}

	public String getFromCode() {
		return fromCode;
	}

	public void setFromCode(String fromCode) {
		this.fromCode = fromCode;
	}

	public String getFromDate() {
		return fromDate;
	}

	public void setFromDate(String fromDate) {
		this.fromDate = fromDate;
	}

	public double getAdultFareOW() {
		return adultFareOW;
	}

	public void setAdultFareOW(double adultFareOW) {
		this.adultFareOW = adultFareOW;
	}

	public double getAdultFareRT() {
		return adultFareRT;
	}

	public void setAdultFareRT(double adultFareRT) {
		this.adultFareRT = adultFareRT;
	}

	public String getAirlinename() {
		return airlinename;
	}

	public void setAirlinename(String airlinename) {
		this.airlinename = airlinename;
	}

	public double getChildFareOW() {
		return childFareOW;
	}

	public void setChildFareOW(double childFareOW) {
		this.childFareOW = childFareOW;
	}

	public double getChildFareRT() {
		return childFareRT;
	}

	public void setChildFareRT(double childFareRT) {
		this.childFareRT = childFareRT;
	}

	public double getInfantFareOW() {
		return infantFareOW;
	}

	public void setInfantFareOW(double infantFareOW) {
		this.infantFareOW = infantFareOW;
	}

	public double getInfantFareRT() {
		return infantFareRT;
	}

	public void setInfantFareRT(double infantFareRT) {
		this.infantFareRT = infantFareRT;
	}

	public String getNotification() {
		return notification;
	}

	public void setNotification(String notification) {
		this.notification = notification;
	}

	public String getAirlineICAOcode() {
		return airlineICAOcode;
	}

	public void setAirlineICAOcode(String airlineICAOcode) {
		this.airlineICAOcode = airlineICAOcode;
	}

	public String getAirlineDesignator() {
		return airlineDesignator;
	}

	public void setAirlineDesignator(String airlineDesignator) {
		this.airlineDesignator = airlineDesignator;
	}

	public String getChargeTaxOnReturnTrip() {
		return chargeTaxOnReturnTrip;
	}

	public void setChargeTaxOnReturnTrip(String chargeTaxOnReturnTrip) {
		this.chargeTaxOnReturnTrip = chargeTaxOnReturnTrip;
	}

	public fare(String type, int count, double tax10w, double tax1rt, double tax20w, double tax2rt, double tax30w,
			double tax3rt, double tax40w, double tax40rt, String toCode, String toDate, String classes, String fromCode,
			String fromDate, double adultFareOW, double adultFareRT, String airlinename, double childFareOW,
			double childFareRT, double infantFareOW, double infantFareRT, String notification, String airlineICAOcode,
			String airlineDesignator, String chargeTaxOnReturnTrip) {
		super();
		this.type = type;
		this.count = count;
		this.tax10W = tax10w;
		this.tax1RT = tax1rt;
		this.tax20W = tax20w;
		this.tax2RT = tax2rt;
		this.tax30W = tax30w;
		this.tax3RT = tax3rt;
		this.tax40W = tax40w;
		this.tax40RT = tax40rt;
		this.toCode = toCode;
		this.toDate = toDate;
		this.classes = classes;
		this.fromCode = fromCode;
		this.fromDate = fromDate;
		this.adultFareOW = adultFareOW;
		this.adultFareRT = adultFareRT;
		this.airlinename = airlinename;
		this.childFareOW = childFareOW;
		this.childFareRT = childFareRT;
		this.infantFareOW = infantFareOW;
		this.infantFareRT = infantFareRT;
		this.notification = notification;
		this.airlineICAOcode = airlineICAOcode;
		this.airlineDesignator = airlineDesignator;
		this.chargeTaxOnReturnTrip = chargeTaxOnReturnTrip;
	}

	@Override
	public String toString() {
		return "fare [type=" + type + ", count=" + count + ", tax10W=" + tax10W + ", tax1RT=" + tax1RT + ", tax20W="
				+ tax20W + ", tax2RT=" + tax2RT + ", tax30W=" + tax30W + ", tax3RT=" + tax3RT + ", tax40W=" + tax40W
				+ ", tax40RT=" + tax40RT + ", toCode=" + toCode + ", toDate=" + toDate + ", classes=" + classes
				+ ", fromCode=" + fromCode + ", fromDate=" + fromDate + ", adultFareOW=" + adultFareOW
				+ ", adultFareRT=" + adultFareRT + ", airlinename=" + airlinename + ", childFareOW=" + childFareOW
				+ ", childFareRT=" + childFareRT + ", infantFareOW=" + infantFareOW + ", infantFareRT=" + infantFareRT
				+ ", notification=" + notification + ", airlineICAOcode=" + airlineICAOcode + ", airlineDesignator="
				+ airlineDesignator + ", chargeTaxOnReturnTrip=" + chargeTaxOnReturnTrip + "]";
	}

}
