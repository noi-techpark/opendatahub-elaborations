// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.file;

import java.io.File;

import java.io.IOException;
import java.net.MalformedURLException;
import org.springframework.stereotype.Service;

import com.opendatahub.constants.GTFSFileNames;

@Service
public class GTFSFile {
	public static void writeFiles() throws IOException, MalformedURLException {
		String fileType = ".txt";
		// File dir = new File(folderPath);

		File dir = GTFSFolder.FOLDER_FILE;
		GTFSFileNames filename = new GTFSFileNames();
		String filePath1 = dir.getAbsolutePath() + "/" + filename.getAgency().toString() + fileType;
		File file1 = new File(filePath1);
		file1.createNewFile();

		String filePath13 = dir.getAbsolutePath() + "/" + filename.getCalendar().toString() + fileType;
		File file13 = new File(filePath13);
		file13.createNewFile();

		String filePath2 = dir.getAbsolutePath() + "/" + filename.getCalendar_dates().toString() + fileType;
		File file2 = new File(filePath2);
		file2.createNewFile();

		// String filePath3 = dir.getAbsolutePath() + "/" + filename.getFare_attributes().toString() + fileType;
		// File file3 = new File(filePath3);
		// file3.createNewFile();

		// String filePath4 = dir.getAbsolutePath() + "/" + filename.getFare_rules().toString() + fileType;
		// File file4 = new File(filePath4);
		// file4.createNewFile();

		// String filePath5 = dir.getAbsolutePath() + "/" + filename.getFeed_info().toString() + fileType;
		// File file5 = new File(filePath5);
		// file5.createNewFile();

		// String filePath6 = dir.getAbsolutePath() + "/" + filename.getFrequencies().toString() + fileType;
		// File file6 = new File(filePath6);
		// file6.createNewFile();

		String filePath7 = dir.getAbsolutePath() + "/" + filename.getRoutes().toString() + fileType;
		File file7 = new File(filePath7);
		file7.createNewFile();

		// String filePath8 = dir.getAbsolutePath() + "/" + filename.getShapes().toString() + fileType;
		// File file8 = new File(filePath8);
		// file8.createNewFile();

		String filePath9 = dir.getAbsolutePath() + "/" + filename.getStop_times().toString() + fileType;
		File file9 = new File(filePath9);
		file9.createNewFile();

		String filePath10 = dir.getAbsolutePath() + "/" + filename.getStops().toString() + fileType;
		File file10 = new File(filePath10);
		file10.createNewFile();

		// String filePath11 = dir.getAbsolutePath() + "/" + filename.getTransfers().toString() + fileType;
		// File file11 = new File(filePath11);
		// file11.createNewFile();

		String filePath12 = dir.getAbsolutePath() + "/" + filename.getTrips().toString() + fileType;
		File file12 = new File(filePath12);
		file12.createNewFile();

	}

	public static void main(String[] args) throws IOException {
		writeFiles();
	}

}
