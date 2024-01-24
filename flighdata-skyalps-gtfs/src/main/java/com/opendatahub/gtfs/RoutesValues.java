// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.gtfs;

public record RoutesValues (
	String route_id, // read specification
	String route_short_name,
	int route_type,// default value 1100
	String agency_id
){
	public static final int ROUTE_TYPE_AIR_SERVICE = 1100;
}
