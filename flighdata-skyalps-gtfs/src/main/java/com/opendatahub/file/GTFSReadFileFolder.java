// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.file;

import java.io.File;
import java.io.IOException;

public class GTFSReadFileFolder {

	public static File Agency;
	public static File Stops;
	public static File Calendar_Dates;
	public static File Calendar;
	public static File Stop_times;
	public static File Trips;
	public static File Routes;
	public static File Fare_rules;

	public static void readFiles() throws IOException {
		File folder = GTFSFolder.FOLDER_FILE;
		File[] listOfFiles = folder.listFiles();
		for (int i = 0; i < listOfFiles.length; i++) {
			if (listOfFiles[i].isFile()) {
				// System.out.println("File " + listOfFiles[i].getName());
				if (listOfFiles[i].getName().equals("agency.txt")) {
					Agency = listOfFiles[i];
					// return listOfFiles[i];
				}
				if (listOfFiles[i].getName().equals("stops.txt")) {
					Stops = listOfFiles[i];
					// return listOfFiles[i];
				}
				if (listOfFiles[i].getName().equals("calendar_dates.txt")) {
					Calendar_Dates = listOfFiles[i];
				}
				if (listOfFiles[i].getName().equals("calendar.txt")) {
					Calendar = listOfFiles[i];
				}
				if (listOfFiles[i].getName().equals("stop_times.txt")) {
					Stop_times = listOfFiles[i];
				}
				if (listOfFiles[i].getName().equals("routes.txt")) {
					Routes = listOfFiles[i];
				}
				if (listOfFiles[i].getName().equals("trips.txt")) {
					Trips = listOfFiles[i];
				}
				if (listOfFiles[i].getName().equals("fare_rules.txt")) {
					Fare_rules = listOfFiles[i];
				}
			} else if (listOfFiles[i].isDirectory()) {
				// System.out.println("Directory " + listOfFiles[i].getName());
			}
		}

	}

	public static void main(String[] args) throws IOException {
		readFiles();
	}

	public static File getAgency() {
		return Agency;
	}

	public static File getStops() {
		return Stops;
	}

	public static File getCalendar_Dates() {
		// TODO Auto-generated method stub
		return Calendar_Dates;
	}

	public static File getCalendar() {
		// TODO Auto-generated method stub
		return Calendar;
	}

	public static File getStop_Times() {
		// TODO Auto-generated method stub
		return Stop_times;
	}

	public static File getTrips() {
		// TODO Auto-generated method stub
		return Trips;
	}

	public static File getRoutes() {
		// TODO Auto-generated method stub
		return Routes;
	}
	
	public static File getFare_rules() {
		// TODO Auto-generated method stub
		return Fare_rules;
	}

}
