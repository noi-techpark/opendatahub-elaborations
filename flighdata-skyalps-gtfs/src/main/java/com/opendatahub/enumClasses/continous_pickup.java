package it.noitechpark.enumClasses;

public enum continous_pickup {
	ContinousStopping_Pickup(0), NoContinousStopping_pickUp(1), MustPhoneAgency(2), MustCoordinateDriver(3);

	private final int value;

	continous_pickup(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static continous_pickup valueOf(int i) {
		if (i == 1) {
			return NoContinousStopping_pickUp;
		} else if (i == 2) {
			return MustPhoneAgency;
		} else if (i == 3) {
			return MustCoordinateDriver;
		} else if (i == 0) {
			return ContinousStopping_Pickup;
		} else {
			return ContinousStopping_Pickup;
		}
	}
}
