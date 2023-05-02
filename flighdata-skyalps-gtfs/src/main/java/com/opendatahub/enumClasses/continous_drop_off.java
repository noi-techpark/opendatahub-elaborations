package com.opendatahub.enumClasses;

public enum continous_drop_off {
	ContinousStopping_DropOff(0), NoContinousStopping_Dropoff(1), MustPhoneAgency(2), MustCoordinateDriver(3);

	private final int value;

	continous_drop_off(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static continous_drop_off valueOf(int i) {
		if (i == 1) {
			return NoContinousStopping_Dropoff;
		} else if (i == 2) {
			return MustPhoneAgency;
		} else if (i == 3) {
			return MustCoordinateDriver;
		} else if (i == 0) {
			return ContinousStopping_DropOff;
		} else {
			return ContinousStopping_DropOff;
		}
	}

}
