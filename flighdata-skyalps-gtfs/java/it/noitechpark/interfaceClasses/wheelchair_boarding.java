package it.noitechpark.interfaceClasses;

import it.noitechpark.enumClasses.child_stops;
import it.noitechpark.enumClasses.parentless_stops;
import it.noitechpark.enumClasses.station_entrances_exits;

public class wheelchair_boarding {

	public static it.noitechpark.enumClasses.parentless_stops getparentlessstops(int parentless_stops2) {

		if (parentless_stops2 == 1) {
			return parentless_stops.Some_vehicles_supported;
		} else if (parentless_stops2 == 2) {
			return parentless_stops.Wheelchair_boarding_not_possible;
		} else if (parentless_stops2 == 0) {
			return parentless_stops.NoInfo;
		} else {
			return parentless_stops.NoInfo;
		}

		// }
		// return null;
	}

	public static it.noitechpark.enumClasses.station_entrances_exits getStation_Entrances_exits(int entrance_exit2) {

		if (entrance_exit2 == 1) {
			return station_entrances_exits.wheelchair_accessible;
		} else if (entrance_exit2 == 2) {
			return station_entrances_exits.not_accessible_path;
		} else if (entrance_exit2 == 0) {
			return station_entrances_exits.As_the_parent_station;
		} else {
			return station_entrances_exits.As_the_parent_station;
		}

		// }
		// return null;
	}

	public static it.noitechpark.enumClasses.child_stops getChildStops(int child_stops2) {

		if (child_stops2 == 1) {
			return child_stops.some_accessible_paths;
		} else if (child_stops2 == 2) {
			return child_stops.some_accessible_other_paths;
		} else if (child_stops2 == 0) {
			return child_stops.As_the_parent_station;
		} else {
			return child_stops.As_the_parent_station;
		}

		// }
		// return null;
	}

}
