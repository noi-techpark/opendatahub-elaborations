package com.opendatahub.service;

import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
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


	public Map<String, ArrayList<StopsValue>> getCSVFile() throws IOException, CsvValidationException {
		Map<String, ArrayList<StopsValue>> multiValueMap = new HashMap<String, ArrayList<StopsValue>>();

		File csv = new File(getClass().getClassLoader().getResource("230406_AirportsCoordinates.csv").getFile());
		boolean csvExists = csv.exists();
		LOG.info("airports.csv exists? {}", csvExists);
		if (csvExists == true) {
			FileInputStream fis = new FileInputStream(csv);
			InputStreamReader isr = new InputStreamReader(fis, "UTF-8");
			CSVReader reader = new CSVReader(isr);
			String[] column;
			int lineNumber = 0;
			while ((column = reader.readNext()) != null) {
				lineNumber++;

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
					/*
					 * String stopId = column[13];
					 * if (!multiValueMap.containsKey(stopId)) {
					 * multiValueMap.put(stopId, new ArrayList<String[]>());
					 * }
					 * String[] latLonPair = {column[4], column[5]};
					 * multiValueMap.get(stopId).add(latLonPair);
					 */
					if (!multiValueMap.containsKey(stopId)) {

						multiValueMap.put(stopId, new ArrayList<StopsValue>());
					}
					multiValueMap.get(stopId).add(stop);
				}
				// multiValueMap.get(stopId).add(column[5]);
				/*
				 * multiValueMap.put(column[13], new ArrayList<String>());
				 * multiValueMap.get(column[13]).add(column[4]);
				 * multiValueMap.get(column[13]).add(column[5]);
				 */

			}

			reader.close();
			isr.close();
			fis.close();

		} else if (csvExists == false) {
			URL url;
			URLConnection con;
			DataInputStream dis;
			FileOutputStream fos;
			byte[] fileData;
			try {
				url = new URL("https://cloud.opendatahub.com/index.php/s/nMCpGfE796Ct77X/download"); // File Location
																										// goes here
				con = url.openConnection(); // open the url connection.
				dis = new DataInputStream(con.getInputStream());
				fileData = new byte[con.getContentLength()];
				for (int q = 0; q < fileData.length; q++) {
					fileData[q] = dis.readByte();
				}
				dis.close(); // close the data input stream
				fos = new FileOutputStream(
						new File(new File(System.getProperty("user.home"), "Desktop"), "airports.csv")); // FILE Save
																											// Location
																											// goes here
				fos.write(fileData); // write out the file we want to save.
				fos.close(); // close the output stream writer
				FileInputStream fis = new FileInputStream(csv);
				InputStreamReader isr = new InputStreamReader(fis, "UTF-8");
				CSVReader reader = new CSVReader(isr);
				String[] column;
				int lineNumber = 0;
				while ((column = reader.readNext()) != null) {
					lineNumber++;
					String stopId = column[13];
					String stopLatString = column[4];
					String stopLonString = column[5];
					if (stopLatString != null && !stopLatString.isEmpty()
							&& stopLonString != null && !stopLonString.isEmpty()) {
						double stopLat = Double.parseDouble(stopLatString);
						double stopLon = Double.parseDouble(stopLonString);
						StopsValue stop = new StopsValue(stopId, stopId, stopId, String.valueOf(stopLat),
								String.valueOf(stopLon));

						/*
						 * String stopId = column[13];
						 * if (!multiValueMap.containsKey(stopId)) {
						 * multiValueMap.put(stopId, new ArrayList<String[]>());
						 * }
						 * String[] latLonPair = {column[4], column[5]};
						 * multiValueMap.get(stopId).add(latLonPair);
						 */
						if (!multiValueMap.containsKey(stopId)) {

							multiValueMap.put(stopId, new ArrayList<StopsValue>());
						}
						multiValueMap.get(stopId).add(stop);
					}
					// multiValueMap.get(stopId).add(column[5]);
					/*
					 * multiValueMap.put(column[13], new ArrayList<String>());
					 * multiValueMap.get(column[13]).add(column[4]);
					 * multiValueMap.get(column[13]).add(column[5]);
					 */

				}

				reader.close();
				isr.close();
				fis.close();
			} catch (Exception m) {
				System.out.println(m);
			}
		}
		return multiValueMap;

	}

}
