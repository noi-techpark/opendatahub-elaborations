package it.noitechpark.enumClasses;

public enum route_color {
	Black(1), White(2), Yellow(3), Red(4), Other(0);

	private final int value;

	route_color(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static route_color valueOf(int i) {
		if (i == 1) {
			return Black;
		} else if (i == 2) {
			return White;
		} else if (i == 3) {
			return Yellow;
		} else if (i == 4) {
			return Red;
		} else if (i == 0) {
			return Other;
		} else {
			return Other;
		}
	}

}
