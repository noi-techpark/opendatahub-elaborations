// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.enumClasses;

public enum location_type {
	Stop_Point(0), Station(1), Stop_Area(1), Entrance(2), Exit(2), Generic_Node(3), Boarding_Area(4);

	private final int value;

	location_type(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static location_type valueOf(int i) {
		if (i == 1) {
			return Station;
		} else if (i == 2) {
			return Entrance;
		} else if (i == 3) {
			return Generic_Node;
		} else if (i == 4) {
			return Boarding_Area;
		} else if (i == 0) {
			return Stop_Point;
		} else {
			return Stop_Point;
		}
	}
}
