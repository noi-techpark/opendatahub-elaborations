// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.gtfs;

import java.net.URL;

public record AgencyValues (
	String agency_id,
	String agency_name,
	URL agency_url,
	String agency_timezone
){}
