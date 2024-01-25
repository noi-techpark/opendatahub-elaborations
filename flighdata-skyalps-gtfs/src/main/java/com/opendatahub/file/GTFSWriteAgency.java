// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.file;

import java.io.FileWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

import com.opendatahub.gtfs.AgencyValues;

public class GTFSWriteAgency {
	public static void writeAgency(ArrayList<AgencyValues> agencyvalueslist) throws Exception {

		GTFSReadFileFolder.readFiles();
		try (FileWriter writer = new FileWriter(GTFSReadFileFolder.getAgency());) {

			String firstLine = "agency_id,agency_name,agency_url,agency_timezone";
			writer.write(firstLine);
			writer.write(System.getProperty("line.separator"));

			Set<AgencyValues> uniqueAgencies = new HashSet<>(agencyvalueslist);

			for (AgencyValues agency : uniqueAgencies) {
				writer.write(agency.agency_name() + ",");
				writer.write(agency.agency_id() + ",");
				writer.write(agency.agency_url().toString() + ",");
				writer.write(agency.agency_timezone().toString());
				writer.write(System.getProperty("line.separator"));
			}
		}
	}
}
