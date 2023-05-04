package com.opendatahub.enumClasses;

public enum stop_sequence {
	Departing_airpot(1), Arrival_airport(2);

	private final int value;

	stop_sequence(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static stop_sequence valueOf(int i) {
		if (i == 1) {
			return Departing_airpot;
		} else if (i == 2) {
			return Arrival_airport;
		} else {
			return null;
		}
	}
	
	public static int intvalueOf(String i) {
		if (i == "Departing_airpot") {
			return 1;
		} else if (i == "Arrival_airport") {
			return 2;
		} else {
			return 1;
		}
	}
	
	public static int flightFromBzo() {
		return 0;
	}
	
	public static int flightToBzo() {
		return 1;
	}
	
	public static int departingairport() {
		return 1;
	}
	
	public static int arrivalairport() {
		return 1;
	}
}
