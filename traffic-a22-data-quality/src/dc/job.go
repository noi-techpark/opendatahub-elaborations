// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package dc

import (
	"os"
	"strconv"
	"strings"
)

var ninjaLimit, _ = strconv.Atoi(os.Getenv("NINJA_QUERY_LIMIT"))

var parentStationType = os.Getenv("EL_PARENT_STATION_TYPE")
var stationType = os.Getenv("EL_STATION_TYPE")
var dataTypes = strings.Split(os.Getenv("EL_DATA_TYPES"), ",")
var periodBase, _ = strconv.Atoi(os.Getenv("EL_BASE_PERIOD"))

const periodAggregate = 86400

func Job() {
	//sumJob()
	combineJob()
	sumUpJob()
}
func sumUpJob() {
	/*
		get all stations that have a parent, and their most recent 1day data
		get the parent's most recent data point
		for all parents where data point is older than children data;
			get history of children with start = most recent parent date
			build children sum
			push to parent
	*/
}
