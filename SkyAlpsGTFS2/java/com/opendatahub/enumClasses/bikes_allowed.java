package com.opendatahub.enumClasses;

public enum bikes_allowed {
	No_bike(0), AtLeast_One_rider_weelchair_allowed(1), No_Riders_In_Wheelchair_allowed(2);

	private final int value;

	bikes_allowed(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static bikes_allowed valueOf(int i) {
		if (i == 1) {
			return AtLeast_One_rider_weelchair_allowed;
		} else if (i == 2) {
			return No_Riders_In_Wheelchair_allowed;
		} else if (i == 0) {
			return No_bike;
		} else {
			return No_bike;
		}
	}

}
