package com.opendatahub.enumClasses;

public enum timepoint {
	Approximate_time(0), Exact_time(1);

	private final int value;

	timepoint(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static timepoint valueOf(int i) {
		if (i == 1) {
			return Exact_time;
		} else if (i == 0) {
			return Approximate_time;
		} else {
			return Approximate_time;
		}
	}

}
