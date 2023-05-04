package com.opendatahub.enumClasses;

public enum wheelchair_accessible {
	No_accessibility_information_available(0), AtLeast_One_rider_weelchair_allowed(1),
	No_Riders_In_Wheelchair_allowed(2);

	private final int value;

	wheelchair_accessible(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static wheelchair_accessible valueOf(int i) {
		if (i == 1) {
			return AtLeast_One_rider_weelchair_allowed;
		} else if (i == 2) {
			return No_Riders_In_Wheelchair_allowed;
		} else if (i == 0) {
			return No_accessibility_information_available;
		} else {
			return No_accessibility_information_available;
		}
	}

}
