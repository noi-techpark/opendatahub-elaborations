package com.opendatahub.service;

import java.io.FileWriter;

import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;

import com.opendatahub.constantsClasses.Calendar;
import com.opendatahub.dto.CalendarValues;

public class GTFSWriteCalendar {

	public static void writeCalendar(ArrayList<CalendarValues> calendarValuesList)
			throws IOException, MalformedURLException, GTFSCheckCalendar {

		Calendar calendar = new Calendar();
		for (int i = 0; i < calendarValuesList.size(); i++) {
			if (calendarValuesList.get(i).getService_id() == null) {
				return;
			}
			if (String.valueOf(calendarValuesList.get(i).getMonday()) == null) {
				return;
			}
			if (String.valueOf(calendarValuesList.get(i).getTuesday()) == null) {
				return;
			}
			if (String.valueOf(calendarValuesList.get(i).getWednesday()) == null) {
				return;
			}
			;
			if (String.valueOf(calendarValuesList.get(i).getThursday()) == null) {
				return;
			}
			if (String.valueOf(calendarValuesList.get(i).getFriday()) == null) {
				return;
			}
			if (String.valueOf(calendarValuesList.get(i).getSaturday()) == null) {
				return;
			}
			if (calendarValuesList.get(i).getStart_date() == null) {
				return;
			}
			if (calendarValuesList.get(i).getEnd_date() == null) {
				return;
			}
		}

		String firstLine = calendar.getService_id() + "," + calendar.getMonday() + "," + calendar.getTuesday() + ","
				+ calendar.getWednesday() + "," + calendar.getThursday() + "," + calendar.getFriday() + ","
				+ calendar.getSaturday() + "," + calendar.getStart_date() + "," + calendar.getEnd_date();

		GTFSReadFileFolder.readFiles();
		FileWriter writer = new FileWriter(GTFSReadFileFolder.getCalendar());
		writer.write(firstLine);
		writer.write(System.getProperty("line.separator"));
		CalendarValues calendarValues = new CalendarValues();
		if(GTFSCheckCalendar.checkcalendarValues(calendarValuesList)) {
		for (int i = 0; i < calendarValuesList.size(); i++) {
			calendarValues.setService_id(calendarValuesList.get(i).getService_id());
			calendarValues.setMonday(calendarValuesList.get(i).getMonday());
			calendarValues.setTuesday(calendarValuesList.get(i).getTuesday());
			calendarValues.setWednesday(calendarValuesList.get(i).getWednesday());
			calendarValues.setThursday(calendarValuesList.get(i).getThursday());
			calendarValues.setFriday(calendarValuesList.get(i).getFriday());
			calendarValues.setSaturday(calendarValuesList.get(i).getSaturday());
			calendarValues.setStart_date(calendarValuesList.get(i).getStart_date());
			calendarValues.setEnd_date(calendarValuesList.get(i).getEnd_date());
			writer.write(calendarValues.getService_id() + ",");
			writer.write(calendarValues.getMonday() + ",");
			writer.write(String.valueOf(calendarValues.getTuesday()) + ",");
			writer.write(String.valueOf(calendarValues.getWednesday()) + ",");
			writer.write(String.valueOf(calendarValues.getThursday()) + ",");
			writer.write(calendarValues.getFriday() + ",");
			writer.write(calendarValues.getSaturday() + ",");
			writer.write(calendarValues.getStart_date() + ",");
			writer.write(calendarValues.getEnd_date() + ",");
			writer.write(System.getProperty("line.separator"));

		}
		writer.close();
		}
	}

	private static void writeCalendar() {
		// TODO Auto-generated method stub

	}

	public static void main(String[] args) throws IOException {
		writeCalendar();
	}

}
