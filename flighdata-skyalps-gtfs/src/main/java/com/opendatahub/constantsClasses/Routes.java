// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.constantsClasses;

public class Routes {

	private String route_id = "route_id";
	private String route_short_name = "route_short_name";
	private String route_type = "route_type";

	public String getRoute_id() {
		return route_id;
	}

	public void setRoute_id(String route_id) {
		this.route_id = route_id;
	}

	public String getRoute_short_name() {
		return route_short_name;
	}

	public void setRoute_short_name(String route_short_name) {
		this.route_short_name = route_short_name;
	}

	public String getRoute_type() {
		return route_type;
	}

	public void setRoute_type(String route_type) {
		this.route_type = route_type;
	}

	@Override
	public String toString() {
		return "Routes [route_id=" + route_id + ", route_short_name=" + route_short_name + ", route_type=" + route_type
				+ "]";
	}


}
