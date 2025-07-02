// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.gtfs;

public record FeedInfoValue (
	String feed_publisher_name,
	String feed_publisher_url,
	String feed_lang
){}
