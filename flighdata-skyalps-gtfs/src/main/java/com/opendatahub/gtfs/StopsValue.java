// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.gtfs;

import java.lang.String;
public record StopsValue (
	String stop_id,
	String stop_code,
	String stop_name,
	String stop_lat,
	String stop_lon
){}

