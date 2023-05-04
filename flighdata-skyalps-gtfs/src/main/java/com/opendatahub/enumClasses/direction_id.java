package com.opendatahub.enumClasses;

public enum direction_id {
	Outbound(0), Inbound(1);

	private final int value;

	direction_id(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static direction_id valueOf(int i) {
		if (i == 1) {
			return Inbound;
		} else if (i == 0) {
			return Outbound;
		} else {
			return Outbound;
		}
	}

}
