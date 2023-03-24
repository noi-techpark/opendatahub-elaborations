package com.opendatahub.service;

import java.io.FileWriter;

import java.io.IOException;
import java.net.MalformedURLException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;

import com.opendatahub.constantsClasses.Calendar_Dates;
import com.opendatahub.dto.Calendar_DatesValues;
import com.opendatahub.enumClasses.exception_type;

public class GTFSWriteCalendar_Dates {

	public static void writeCalendar_Dates(ArrayList<Calendar_DatesValues> calendarValuesList)
			throws IOException, MalformedURLException, GTFSCheckCalendarDates {
		Calendar_Dates calendar = new Calendar_Dates();
		Date date = new Date();
		SimpleDateFormat format = new SimpleDateFormat("yyyy_MM_dd_HH.mm.ss");

		String currentDateTime = format.format(date);
		for (int i = 0; i < calendarValuesList.size(); i++) {
			if (calendarValuesList.get(i).getService_id() == null) {
				calendarValuesList.get(i).setService_id("empty");
			}
			if (calendarValuesList.get(i).getException_type() == null) {
				calendarValuesList.get(i).setException_type(exception_type.valueOf(0));
			}
			if (calendarValuesList.get(i).getDate() == null) {
				calendarValuesList.get(i).setDate(format);
			}
		}

		String firstLine = calendar.getService_id() + "," + calendar.getException_type() + "," + calendar.getDate();

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getCalendar_Dates());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		Calendar_DatesValues calendarValues = new Calendar_DatesValues();
		if(GTFSCheckCalendarDates.checkCalendarDatesMandatoryFields(calendarValuesList)) {
		for (int i = 0; i < calendarValuesList.size(); i++) {
			calendarValues.setService_id(calendarValuesList.get(i).getService_id());
			calendarValues.setException_type(calendarValuesList.get(i).getException_type());
			calendarValues.setDate(calendarValuesList.get(i).getDate());
			writer.write(calendarValues.getService_id() + ",");
			writer.write(calendarValues.getException_type() + ",");
			writer.write(calendarValues.getDate().toLocalizedPattern());
			writer.write(System.getProperty("line.separator"));
		}
		writer.close();
		}
	}

	private static void writeCalendar_Dates() {
		// TODO Auto-generated method stub

	}

	public static void main(String[] args) throws IOException {
		writeCalendar_Dates();
	}

}
