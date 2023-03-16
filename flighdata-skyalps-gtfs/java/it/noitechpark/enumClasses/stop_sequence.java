package it.noitechpark.enumClasses;

public enum stop_sequence {
	Departing_airpot(1), Arrival_airport(2);

	private final int value;

	stop_sequence(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static stop_sequence valueOf(int i) {
		if (i == 1) {
			return Departing_airpot;
		} else if (i == 2) {
			return Arrival_airport;
		} else {
			return null;
		}
	}
}
