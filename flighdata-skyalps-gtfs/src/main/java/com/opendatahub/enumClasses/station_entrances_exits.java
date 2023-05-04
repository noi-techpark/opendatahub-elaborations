package com.opendatahub.enumClasses;

public enum station_entrances_exits {
	As_the_parent_station(0), wheelchair_accessible(1), not_accessible_path(2);

	private final int value;

	station_entrances_exits(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static station_entrances_exits valueOf(int i) {
		if (i == 1) {
			return wheelchair_accessible;
		} else if (i == 2) {
			return not_accessible_path;
		} else if (i == 0) {
			return As_the_parent_station;
		} else {
			return As_the_parent_station;
		}
	}

}
