// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package dc

import (
	"os"
	"strconv"

	"github.com/noi-techpark/go-bdp-client/bdplib"
)

var sumRequestLimit, _ = strconv.Atoi(os.Getenv("NINJA_QUERY_LIMIT"))
var parentStationType = os.Getenv("EL_PARENT_STATION_TYPE")
var baseStationType = os.Getenv("EL_STATION_TYPE")

// Base data types to aggregate by day
var aggrDataTypes = map[string]struct{}{"Nr. Light Vehicles": {}, "Nr. Heavy Vehicles": {}, "Nr. Buses": {}, "Nr. Equivalent Vehicles": {}}

// Not all data types are counted in total vehicles. Equivalent Vehicles are already a type of total
var totalDataTypes = map[string]struct{}{"Nr. Light Vehicles": {}, "Nr. Heavy Vehicles": {}, "Nr. Buses": {}}
var basePeriod, _ = strconv.Atoi(os.Getenv("EL_BASE_PERIOD"))

// aggregate by day. Cannot be changed without also changing the code to something more generic instead of 1 day
const periodAgg = 86400
const origin = "A22"

var TotalType = bdplib.CreateDataType("Nr. Vehicles", "", "Number of vehicles", "total")

var bdp bdplib.Bdp

func syncDataTypes() {
	bdp.SyncDataTypes(baseStationType, []bdplib.DataType{TotalType})
}

func Job() {
	bdp = *bdplib.FromEnv()
	syncDataTypes()
	combineJob()
	sumJob()
	sumParentJob()
}
