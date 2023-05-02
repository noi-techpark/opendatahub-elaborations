package com.opendatahub.enumClasses;

public enum agency_timezone {
	EuropeRome(1), Other(2);

	private final int value;

	agency_timezone(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static agency_timezone valueOf(int i) {
		if (i == 1) {
			return EuropeRome;
		} else if (i == 2) {
			return Other;
		} else {
			return null;
		}
	}

}
