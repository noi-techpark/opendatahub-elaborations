// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package dc

import (
	"os"
	"strconv"
	"strings"
	"traffic-a22-data-quality/bdplib"
)

var sumRequestLimit, _ = strconv.Atoi(os.Getenv("NINJA_QUERY_LIMIT"))
var parentStationType = os.Getenv("EL_PARENT_STATION_TYPE")
var baseStationType = os.Getenv("EL_STATION_TYPE")
var baseDataTypes = strings.Split(os.Getenv("EL_DATA_TYPES"), ",")
var basePeriod, _ = strconv.Atoi(os.Getenv("EL_BASE_PERIOD"))

const periodAgg = 86400
const origin = "A22"

var TotalType = bdplib.CreateDataType("Nr. Vehicles", "", "Number of vehicles", "total")

func syncDataTypes() {
	bdplib.SyncDataTypes(baseStationType, []bdplib.DataType{TotalType})
}

func Job() {
	syncDataTypes()
	combineJob()
	sumJob()
	sumParentJob()
}
