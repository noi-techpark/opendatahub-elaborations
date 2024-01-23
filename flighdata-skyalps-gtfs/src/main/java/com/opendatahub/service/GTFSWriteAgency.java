// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.service;

import java.io.FileWriter;

import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.opendatahub.constantsClasses.Agency;
import com.opendatahub.constantsClasses.DefaultValues;
import com.opendatahub.dto.AgencyValues;
import com.opendatahub.enumClasses.agency_lang;
import com.opendatahub.enumClasses.agency_timezone;

public class GTFSWriteAgency {
	public static void writeAgency(ArrayList<AgencyValues> agencyvalueslist)
			throws IOException, MalformedURLException, GTFSCheckAgency {

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
				agencyvalueslist.get(i)
						.setAgency_timezone(DefaultValues.getDefaultAgencyTimeZone_Value());
			}
		}

		String firstLine = agency.getAgencyname() + "," + agency.getAgency_url() + ","
				+ agency.getAgency_timezone();

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getAgency());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		AgencyValues agencyvaluesobject = new AgencyValues();
		if (GTFSCheckAgency.checkAgencyMandatoryFields(agencyvalueslist)) {
			// System.out.println("Before removing duplicates : " +
			// Arrays.toString(agencyvalueslist.toArray()));

			final List<AgencyValues> listWithoutDuplicates = new ArrayList<>(
					new HashSet<>(agencyvalueslist));

			Set<AgencyValues> uniqueAgencies = new HashSet<>(agencyvalueslist);

			// System.out.println("After removing duplicates :: "
			// + Arrays.toString(uniqueAgencies.toArray()));

			/*
			 * for (int i = 0; i < uniqueAgencies.size(); i++) {
			 * agencyvaluesobject.setAgency_name(agencyvalueslist.get(i).getAgency_name());
			 * agencyvaluesobject.setAgency_url(agencyvalueslist.get(i).getAgency_url());
			 * agencyvaluesobject.setAgency_timezone(agencyvalueslist.get(i).
			 * getAgency_timezone());
			 * writer.write(agencyvaluesobject.getAgency_name() + ",");
			 * writer.write(agencyvaluesobject.getAgency_url().toString() + ",");
			 * writer.write(agencyvaluesobject.getAgency_timezone().toString() + ",");
			 * writer.write(System.getProperty("line.separator"));
			 * 
			 * }
			 * writer.close();
			 */
			for (AgencyValues agency2 : uniqueAgencies) {
				/*
				 * agencyvaluesobject.setAgency_name(agencyvalueslist.get(i).getAgency_name());
				 * agencyvaluesobject.setAgency_url(agencyvalueslist.get(i).getAgency_url());
				 * agencyvaluesobject.setAgency_timezone(agencyvalueslist.get(i).
				 * getAgency_timezone());
				 */
				writer.write(agency2.getAgency_name() + ",");
				writer.write(agency2.getAgency_url().toString() + ",");
				writer.write(agency2.getAgency_timezone().toString());
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
