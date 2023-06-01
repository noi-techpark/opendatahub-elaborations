// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.enumClasses;

public enum pickup_type {
	Regularly_scheduled_pickup(0), No_pickup_available(1), Phone_agency_to_arrange(2),
	Coordinate_with_driver_to_arrange(3);

	private final int value;

	pickup_type(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static pickup_type valueOf(int i) {
		if (i == 1) {
			return No_pickup_available;
		} else if (i == 2) {
			return Phone_agency_to_arrange;
		} else if (i == 3) {
			return Coordinate_with_driver_to_arrange;
		} else if (i == 0) {
			return Regularly_scheduled_pickup;
		} else {
			return Regularly_scheduled_pickup;
		}
	}
}
