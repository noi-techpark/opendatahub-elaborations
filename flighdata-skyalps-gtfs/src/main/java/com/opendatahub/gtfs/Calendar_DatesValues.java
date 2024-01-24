// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.gtfs;

public record Calendar_DatesValues(
	String service_id, // reference to service_id given in calendar.txt. To be left empty.
	String date // date when service exception occurs. To be left empty.
){}
