// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.gtfs;
import java.lang.String;

//https://gtfs.org/schedule/reference/#stop_timestxt
public record Stop_TimesValues(
	String trip_id,
	String arrival_time,
	String departure_time,
	String stop_id,
	int stop_sequence,
	Timepoint timepoint) {}
