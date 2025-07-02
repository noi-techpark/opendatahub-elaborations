// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.gtfs;

public record TripsValues (
	String route_id, // read specifications
	String service_id,
	String trip_id, // scode
	int direction_id,// Check if the in the ODH API if a flight departs from Bolzano (in this case
								// value is 0) or arrives to Bolzano (int his case value is 1)
	String shape_id
){}
