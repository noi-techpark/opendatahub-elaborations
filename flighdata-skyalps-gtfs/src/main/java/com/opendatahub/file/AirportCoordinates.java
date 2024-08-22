// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.file;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.util.ObjectUtils;

import com.opencsv.CSVReader;
import com.opendatahub.gtfs.StopsValue;

@Service
public class AirportCoordinates {

	private static final Logger LOG = LoggerFactory.getLogger(AirportCoordinates.class);

	// start with / to read from resources directory; with no / it reads current class package 
	private final String CSV_PATH = "/AirportsCoordinates.csv";

	public Map<String, StopsValue> getCSVFile() throws Exception {
		Map<String, StopsValue> multiValueMap = new HashMap<String, StopsValue>();

		LOG.debug("Reading {}...", CSV_PATH);

		try(
			InputStream input = getClass().getResourceAsStream(CSV_PATH);
			InputStreamReader isr = new InputStreamReader(input, "UTF-8");
			CSVReader reader = new CSVReader(isr);
		) {
			String[] column;
			while ((column = reader.readNext()) != null) {
				String iataCode = column[13];
				String stopLatString = column[4];
				String stopLonString = column[5];
				if (!ObjectUtils.isEmpty(iataCode) && stopLatString != null && !stopLatString.isEmpty()
						&& stopLonString != null && !stopLonString.isEmpty() && !stopLatString.equals("latitude_deg") &&
						!stopLonString.equals("longitude_deg")) {
					double stopLat = Double.parseDouble(stopLatString);
					double stopLon = Double.parseDouble(stopLonString);

					StopsValue stop = new StopsValue(iataCode, iataCode, iataCode, String.valueOf(stopLat), String.valueOf(stopLon));

					if (!multiValueMap.containsKey(iataCode)) {
						multiValueMap.put(iataCode, stop);
					} else {
						throw new Exception("Duplicate mapping for Airport " + iataCode);
					}
				}
			}
		}

		LOG.debug("Reading {} done.", CSV_PATH);

		return multiValueMap;

	}

}
