// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.gtfs;

public record ShapeValue (
	String shape_id,
	String shape_pt_lat,
	String shape_pt_lon,
	int shape_pt_sequence,
	String shape_dist_traveled
){}
