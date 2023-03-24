package com.opendatahub.dto;

import java.io.Serializable;
import java.lang.String;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
@JsonIgnoreProperties(ignoreUnknown = true)
public class Data implements Serializable {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private boolean sactive;
	private boolean savailable;
	private String scode;
	private Map<String, Double> scoordinate;
	private Smetadata smetadata;
	private String sname;
	private String sorigin;
	private String stype;

	public Data() {

	}

	public boolean isSactive() {
		return sactive;
	}

	public void setSactive(boolean sactive) {
		this.sactive = sactive;
	}

	public boolean isSavailable() {
		return savailable;
	}

	public void setSavailable(boolean savailable) {
		this.savailable = savailable;
	}

	public String getScode() {
		return scode;
	}

	public void setScode(String scode) {
		this.scode = scode;
	}

	public Map<String, Double> getScoordinate() {
		return scoordinate;
	}

	public void setScoordinate(Map<String, Double> scoordinate) {
		this.scoordinate = scoordinate;
	}

	public Smetadata getSmetadata() {
		return smetadata;
	}

	public void setSmetadata(Smetadata smetadata) {
		this.smetadata = smetadata;
	}

	public String getSname() {
		return sname;
	}

	public void setSname(String sname) {
		this.sname = sname;
	}

	public String getSorigin() {
		return sorigin;
	}

	public void setSorigin(String sorigin) {
		this.sorigin = sorigin;
	}

	public String getStype() {
		return stype;
	}

	public void setStype(String stype) {
		this.stype = stype;
	}

	public Data(boolean sactive, boolean savailable, String scode, Map<String, Double> scoordinate, Smetadata smetadata,
			String sname, String sorigin, String stype) {
		super();
		this.sactive = sactive;
		this.savailable = savailable;
		this.scode = scode;
		this.scoordinate = scoordinate;
		this.smetadata = smetadata;
		this.sname = sname;
		this.sorigin = sorigin;
		this.stype = stype;
	}

	@Override
	public String toString() {
		return "Data [sactive=" + sactive + ", savailable=" + savailable + ", scode=" + scode + ", scoordinate="
				+ scoordinate + ", smetadata=" + smetadata + ", sname=" + sname + ", sorigin=" + sorigin + ", stype="
				+ stype + "]";
	}

}
