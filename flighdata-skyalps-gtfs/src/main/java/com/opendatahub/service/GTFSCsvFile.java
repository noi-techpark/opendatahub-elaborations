package com.opendatahub.service;

import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvValidationException;
import com.opendatahub.dto.StopsValue;

@Service
public class GTFSCsvFile {

	private static final Logger LOG = LoggerFactory.getLogger(GTFSCsvFile.class);

	// start with / to read from resources directory; with no / it reads current class package 
	private final String CSV_PATH = "/AirportsCoordinates.csv";

	public Map<String, ArrayList<StopsValue>> getCSVFile() throws IOException, CsvValidationException {
		Map<String, ArrayList<StopsValue>> multiValueMap = new HashMap<String, ArrayList<StopsValue>>();

		LOG.debug("Reading {}...", CSV_PATH);
		InputStream input = getClass().getResourceAsStream(CSV_PATH);

		InputStreamReader isr = new InputStreamReader(input, "UTF-8");
		CSVReader reader = new CSVReader(isr);
		String[] column;
		while ((column = reader.readNext()) != null) {

			String stopId = column[13];
			String stopLatString = column[4];
			String stopLonString = column[5];
			if (stopLatString != null && !stopLatString.isEmpty()
					&& stopLonString != null && !stopLonString.isEmpty() && !stopLatString.equals("latitude_deg") &&
					!stopLonString.equals("longitude_deg")) {
				double stopLat = Double.parseDouble(stopLatString);
				double stopLon = Double.parseDouble(stopLonString);

				StopsValue stop = new StopsValue(stopId, stopId, stopId, String.valueOf(stopLat),
						String.valueOf(stopLon));

				if (!multiValueMap.containsKey(stopId)) {

					multiValueMap.put(stopId, new ArrayList<StopsValue>());
				}
				multiValueMap.get(stopId).add(stop);
			}
		}

		reader.close();
		isr.close();

		LOG.debug("Reading {} done.", CSV_PATH);

		return multiValueMap;

	}

}
