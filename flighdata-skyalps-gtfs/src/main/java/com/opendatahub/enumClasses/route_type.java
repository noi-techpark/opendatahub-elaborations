package com.opendatahub.enumClasses;

public enum route_type {
	Tram_StreetCar_LightRail(0), Subway_metro(1), Rail(2), Bus(3), Ferry(4), Cable_tram(5),
	AerialLift_SuspendedCableCar(6), Funicular(7), Trolleybus(8), Monorail(9);

	private final int value;

	route_type(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static route_type valueOf(int i) {
		if (i == 1) {
			return Subway_metro;
		} else if (i == 2) {
			return Rail;
		} else if (i == 3) {
			return Bus;
		} else if (i == 4) {
			return Ferry;
		} else if (i == 5) {
			return Cable_tram;
		} else if (i == 6) {
			return AerialLift_SuspendedCableCar;
		} else if (i == 7) {
			return Funicular;
		} else if (i == 8) {
			return Trolleybus;
		} else if (i == 9) {
			return Monorail;
		} else if (i == 0) {
			return Tram_StreetCar_LightRail;
		} else {
			return Tram_StreetCar_LightRail;
		}
	}
	
	public static int defaultValue() {
		return Integer.valueOf("1100");
	}
	
	public static int intValueOf(String i) {
		if(i == "Subway") {
			return 1;
		} else if(i == "Tram") {
			return 0;
		} if(i == "Streetcar") {
			return 0;
		} else if(i == "Light rail") {
			return 0;
		} if(i == "Metro") {
			return 1;
		} else if(i == "Rail") {
			return 2;
		} if(i == "Bus") {
			return 3;
		} else if(i == "Ferry") {
			return 4;
		} if(i == "Cable tram") {
			return 5;
		} else if(i == "Aerial lift") {
			return 6;
		} if(i == "suspended cable car") {
			return 6;
		} else if(i == "Funicular") {
			return 7;
		} if(i == "Trolleybus") {
			return 11;
		} else if(i == "Monorail") {
			return 12;
		} else if(i == "Default" || i == null) {
		return 1100; 
		} else {
			return 1100;
		}
	}

}
