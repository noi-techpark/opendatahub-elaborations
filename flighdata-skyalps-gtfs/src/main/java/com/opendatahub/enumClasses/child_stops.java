package com.opendatahub.enumClasses;

public enum child_stops {
	As_the_parent_station(0), some_accessible_paths(1), some_accessible_other_paths(2);

	private final int value;

	child_stops(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static child_stops valueOf(int i) {
		if (i == 1) {
			return some_accessible_paths;
		} else if (i == 2) {
			return some_accessible_other_paths;
		} else if (i == 0) {
			return As_the_parent_station;
		} else {
			return As_the_parent_station;
		}
	}
}
