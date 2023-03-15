package it.noitechpark.enumClasses;

public enum continous_pickup_stopTimes {
	Continous_stopping_pickup(0), Continous_stop_pickup(1), Phone_agency_to_arrange(2),
	Coordinate_with_driver_to_arrange(3);

	private final int value;

	continous_pickup_stopTimes(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static continous_pickup_stopTimes valueOf(int i) {
		if (i == 1) {
			return Continous_stop_pickup;
		} else if (i == 2) {
			return Phone_agency_to_arrange;
		} else if (i == 3) {
			return Coordinate_with_driver_to_arrange;
		} else if (i == 0) {
			return Continous_stopping_pickup;
		} else {
			return Continous_stopping_pickup;
		}
	}
}
