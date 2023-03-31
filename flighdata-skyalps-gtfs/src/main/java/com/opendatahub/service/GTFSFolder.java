package com.opendatahub.service;

import java.io.File;

import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

import org.springframework.stereotype.Service;

@Service
public class GTFSFolder {

	// private static final DateFormat SDF = new
	// SimpleDateFormat("yyyy_MM_dd_HH_mm_ss");
	// public static final File FOLDER_FILE = new File(new
	// File(System.getProperty("user.home")), "GTFS_" + SDF.format(new Date()));

	public static final File FOLDER_FILE = new File(new File(System.getProperty("user.home")), "GTFS");

	public static void writeRequestAndResponse() throws IOException {
		File theDir = FOLDER_FILE;
		/*
		 * Date date = new Date();
		 * SimpleDateFormat format = new SimpleDateFormat("yyyy_MM_dd_HH.mm.ss");
		 * 
		 * String currentDateTime = format.format(date);
		 * 
		 * String folderPath = "C:\\Users\\39351\\Desktop\\" + "GTFS_" +
		 * currentDateTime;
		 * 
		 * File theDir = new File(folderPath);
		 */

		// if the directory does not exist, create it
		if (!theDir.exists()) {
			// System.out.println("creating directory: " + theDir.getName());
			boolean result = false;

			try {

				theDir.mkdirs();

				result = true;
			} catch (SecurityException se) {
				// handle it
				System.out.println(se.getMessage());
			}
			if (result) {
				System.out.println("Folder created");
			}
		} else if (theDir.exists()) {

			System.out.println("Folder exist");
		}

	}

	public static void main(String[] args) throws IOException {
		writeRequestAndResponse();
	}

}
