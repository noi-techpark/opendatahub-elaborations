// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.parser;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.domain.ParkingObservation;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/**
 * @author mreinstadler This is a utility class for writing arff to file. This
 * is only useful for tests with weka, since Weka requires arff and this provides
 * correct arff files
 * 
 */
class ArffFileWriter {
	
	private static final Log logger = LogFactory.getLog(ArffFileWriter.class);

	/**
	 * @param arffString
	 *            the arff string to be written to file
	 * @param pid
	 *            the id of the parking place where the id is the file name
	 * @param periodicity the time distance between {@link ParkingObservation}
	 * @throws IOException
	 */
	public static void writeArffToFile(String arffString, String pid, ObservationPeriodicity periodicity, 
			TSModelConfig config){
		logger.info("Write the arff string of parking place " +pid + " to file");
		File file = new File(config.getArffFileDirectory()
				+ File.separator + pid +"_"+periodicity.toString()+ ".arff");
		try {
			file.createNewFile();
			BufferedWriter out = new BufferedWriter(new FileWriter(file));
			out.write(arffString);
			out.close();
			logger.info("Finish to write the arff string of parking place " +pid + " to file");
		} catch (IOException e) {
			logger.warn("could not write arff to file");
			return;
		}
		
		
	}

}
