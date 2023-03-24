package com.opendatahub.enumClasses;

public enum exception_type {

	Service_added_for_the_specified_date(1), Service_removed_for_the_specified_date(2), empty(0);

	private final int value;

	exception_type(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static exception_type valueOf(int i) {
		if (i == 1) {
			return Service_added_for_the_specified_date;
		} else if (i == 2) {
			return Service_removed_for_the_specified_date;
		} else {
			return empty;
		}
	}
}
