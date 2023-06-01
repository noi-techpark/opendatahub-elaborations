// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsforecast.entity;
import java.util.HashMap;


/**
 * @author mreinstadler
 * this class represents one single parkingplace as {@link ObservationMetaInfo} object
 * In this way it can be retrieved from the database and used as meta information
 * to the parking observations
 *
 */
public class ParkingPlace implements ObservationMetaInfo{

	private String name = "";
	private int maxSlots = -1;
	private String parkingId;
	private String phone = "";
	private String adress = "";
	private String description = "";
	private double latitude = -1;
	private double longitude = -1;


	/**
	 * @param metadata
	 *            a {@link HashMap} of objects, which correstpond to the name
	 *            and value of the metadata
	 */
	public ParkingPlace(HashMap<String, Object> metadata) {
		this.phone = (String) metadata.get("phone");
		String lineseparator = System.getProperty("line.separator");
		this.phone.replace(lineseparator, "").trim();
		this.adress = (String) metadata.get("address");
		this.adress = adress.replace(lineseparator, "").trim();
		this.maxSlots = (Integer) metadata.get("slots");
		this.name = (String) metadata.get("name");
		this.name = name.replace(lineseparator, "").trim();
		this.description = (String) metadata.get("description");
		this.description = description.replace(lineseparator, "").trim();
		this.longitude = (Double) metadata.get("longitude");
		this.latitude = (Double) metadata.get("latitude");
	}

	/**
	 * @param id
	 *            the id of the parking place
	 * @param phone
	 *            the phone number of the parking place
	 * @param adress
	 *            the adress of the parking place
	 * @param slots
	 *            the maximum free slots of the parking place
	 * @param description
	 *            the description of the parking place
	 * @param name
	 *            the name of the parking place
	 * @param longitude
	 *            the longitude of the parking place
	 * @param latitude
	 *            the latitude of the parking place
	 */
	public ParkingPlace(String id, String phone, String adress, int slots,
			String description, String name, double longitude, double latitude) {
		this.parkingId = id;
		this.phone = phone;
		this.adress = adress;
		this.maxSlots = slots;
		this.description = description;
		this.name = name;
		this.longitude = longitude;
		this.latitude = latitude;
	}

	/**
	 * @param id
	 *            the id of the parking place
	 * @param maxSlots
	 *            the maximum number of available slots in the parking place
	 */
	public ParkingPlace(int id, int maxSlots) {
		String UNKNOWN = "unknown";
		this.parkingId = String.valueOf(id);
		this.phone = UNKNOWN;
		this.adress = UNKNOWN;
		this.maxSlots = maxSlots;
		this.description = UNKNOWN;
		this.name = UNKNOWN;
		this.longitude = 0.0;
		this.latitude = 0.0;
	}

	/**
	 * @return the name
	 */
	public String getName() {
		return name;
	}

	/**
	 * @param name the name to set
	 */
	public void setName(String name) {
		this.name = name;
	}

	/**
	 * @return the maxSlots
	 */
	public int getMaxSlots() {
		return maxSlots;
	}

	/**
	 * @param maxSlots the maxSlots to set
	 */
	public void setMaxSlots(int maxSlots) {
		this.maxSlots = maxSlots;
	}

	/**
	 * @return the parkingId
	 */
	public String getParkingId() {
		return parkingId;
	}

	/**
	 * @param parkingId the parkingId to set
	 */
	public void setParkingId(String parkingId) {
		this.parkingId = parkingId;
	}

	/**
	 * @return the phone
	 */
	public String getPhone() {
		return phone;
	}

	/**
	 * @param phone the phone to set
	 */
	public void setPhone(String phone) {
		this.phone = phone;
	}

	/**
	 * @return the adress
	 */
	public String getAdress() {
		return adress;
	}

	/**
	 * @param adress the adress to set
	 */
	public void setAdress(String adress) {
		this.adress = adress;
	}

	/**
	 * @return the description
	 */
	public String getDescription() {
		return description;
	}

	/**
	 * @param description the description to set
	 */
	public void setDescription(String description) {
		this.description = description;
	}

	/**
	 * @return the latitude
	 */
	public double getLatitude() {
		return latitude;
	}

	/**
	 * @param latitude the latitude to set
	 */
	public void setLatitude(double latitude) {
		this.latitude = latitude;
	}

	/**
	 * @return the longitude
	 */
	public double getLongitude() {
		return longitude;
	}

	/**
	 * @param longitude the longitude to set
	 */
	public void setLongitude(double longitude) {
		this.longitude = longitude;
	}
	
	
	

	

}
