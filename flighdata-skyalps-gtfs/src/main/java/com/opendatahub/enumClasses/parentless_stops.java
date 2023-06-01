// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.enumClasses;

public enum parentless_stops {
	NoInfo(0), Some_vehicles_supported(1), Wheelchair_boarding_not_possible(2);

	private final int value;

	parentless_stops(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static parentless_stops valueOf(int i) {
		if (i == 1) {
			return Some_vehicles_supported;
		} else if (i == 2) {
			return Wheelchair_boarding_not_possible;
		} else if (i == 0) {
			return NoInfo;
		} else {
			return NoInfo;
		}
	}

}
