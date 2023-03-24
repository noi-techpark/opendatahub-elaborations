package com.opendatahub.service;

import java.io.FileWriter;

import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;

import com.opendatahub.constantsClasses.Agency;
import com.opendatahub.constantsClasses.DefaultValues;
import com.opendatahub.dto.AgencyValues;
import com.opendatahub.enumClasses.agency_lang;
import com.opendatahub.enumClasses.agency_timezone;

public class GTFSWriteAgency {
	public static void writeAgency(ArrayList<AgencyValues> agencyvalueslist) throws IOException, MalformedURLException, GTFSCheckAgency {

		Agency agency = new Agency();
		for (int i = 0; i < agencyvalueslist.size(); i++) {
			if (agencyvalueslist.get(i).getAgency_name() == null) {
				// System.out.println("Agency_name is mandatory. Passing default value:
				// SkyAlps");
				agencyvalueslist.get(i).setAgency_name(DefaultValues.getDefaultAgency_nameValue());
			}
			if (agencyvalueslist.get(i).getAgency_url() == null) {
				// System.out.println("Agency_url is mandatory. Passing default value:
				// https://www.skyalps.com");
				agencyvalueslist.get(i).setAgency_url(new URL(DefaultValues.getDefultAgency_urlValue()));
			}
			if (agencyvalueslist.get(i).getAgency_timezone() == null) {
				// System.out.println("Agency_timezone is mandatory. Passing default value:
				// Rome");
				agencyvalueslist.get(i).setAgency_timezone(agency_timezone.valueOf(DefaultValues.getDefaultAgencyTimeZone_Value()));
			}
			if (agencyvalueslist.get(i).getAgency_id() == null) {
				agencyvalueslist.get(i).setAgency_id("null");
			}
			;
			if (agencyvalueslist.get(i).getAgency_lang() == null) {
				agencyvalueslist.get(i).setAgency_lang(agency_lang.valueOf(DefaultValues.getDefaultAgencyLangValue()));
			}
			if (agencyvalueslist.get(i).getAgency_phone() == null) {
				agencyvalueslist.get(i).setAgency_phone("null");
			}
			if (agencyvalueslist.get(i).getAgency_fare_url() == null) {
				agencyvalueslist.get(i).setAgency_fare_url(new URL(DefaultValues.getDefultAgency_urlValue()));
			}
			if (agencyvalueslist.get(i).getAgency_email() == null) {
				agencyvalueslist.get(i).setAgency_email("null");
			}
		}

		String firstLine = agency.getAgency_id() + "," + agency.getAgencyname() + "," + agency.getAgency_url() + ","
				+ agency.getAgency_timezone() + "," + agency.getAgency_lang() + "," + agency.getAgency_fare_url() + ","
				+ agency.getAgency_phone() + "," + agency.getAgency_email();

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getAgency());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		AgencyValues agencyvaluesobject = new AgencyValues();
		if(GTFSCheckAgency.checkAgencyMandatoryFields(agencyvalueslist)) {
		for (int i = 0; i < agencyvalueslist.size(); i++) {
			agencyvaluesobject.setAgency_id(agencyvalueslist.get(i).getAgency_id());
			agencyvaluesobject.setAgency_name(agencyvalueslist.get(i).getAgency_name());
			agencyvaluesobject.setAgency_url(agencyvalueslist.get(i).getAgency_url());
			agencyvaluesobject.setAgency_timezone(agencyvalueslist.get(i).getAgency_timezone());
			agencyvaluesobject.setAgency_lang(agencyvalueslist.get(i).getAgency_lang());
			agencyvaluesobject.setAgency_phone(agencyvalueslist.get(i).getAgency_phone());
			agencyvaluesobject.setAgency_fare_url(agencyvalueslist.get(i).getAgency_fare_url());
			agencyvaluesobject.setAgency_email(agencyvalueslist.get(i).getAgency_email());
			writer.write(agencyvaluesobject.getAgency_id() + ",");
			writer.write(agencyvaluesobject.getAgency_name() + ",");
			writer.write(agencyvaluesobject.getAgency_url().toString() + ",");
			writer.write(agencyvaluesobject.getAgency_timezone().toString() + ",");
			writer.write(agencyvaluesobject.getAgency_lang().toString() + ",");
			writer.write(agencyvaluesobject.getAgency_phone() + ",");
			writer.write(agencyvaluesobject.getAgency_fare_url().toExternalForm() + ",");
			writer.write(agencyvaluesobject.getAgency_email());
			writer.write(System.getProperty("line.separator"));

		}
		writer.close();
		}
	}

	private static void writeAgency() {
		// TODO Auto-generated method stub

	}

	public static void main(String[] args) throws IOException {
		writeAgency();
	}
}
