// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"context"
	"fmt"
	"log/slog"
	"maps"
	"slices"
	"strconv"
	"strings"

	"github.com/noi-techpark/go-bdp-client/bdplib"
	"github.com/noi-techpark/go-timeseries-client/odhts"
	"github.com/noi-techpark/opendatahub-go-sdk/ingest/ms"
	"github.com/noi-techpark/opendatahub-go-sdk/tel"
	"github.com/robfig/cron/v3"
)

var env struct {
	LOG_LEVEL         string
	CRON              string
	NINJA_BASEURL     string
	NINJA_REFERER     string
	ODH_TOKEN_URL     string
	ODH_CLIENT_ID     string
	ODH_CLIENT_SECRET string
}

func main() {
	ms.InitWithEnv(context.Background(), "", &env)
	slog.Info("Starting air-quality-rating elaboration...")
	defer tel.FlushOnPanic()

	b := bdplib.FromEnv()

	n := odhts.NewCustomClient(env.NINJA_BASEURL, env.ODH_TOKEN_URL, "el-air-quality-rating")
	n.UseAuth(env.ODH_CLIENT_ID, env.ODH_CLIENT_SECRET)

	c := cron.New(cron.WithSeconds())
	c.AddFunc(env.CRON, func() {

		req := odhts.DefaultRequest()
		req.Repr = odhts.TreeNode
		req.AddStationType("EnvironmentStation")
		req.DataTypes = []string{"PM10_raw,CO_raw"}
		req.Limit = -1
		req.Select = "mperiod,mvalidtime,mtransactiontime,pcode"
		req.Where = fmt.Sprintf("and(sactive.eq.true,mperiod.in.(%d,%d))", 600, 3600)

		var res odhts.Response[NinjaTreeData]
		err := odhts.Latest(n, req, &res)
		if err != nil {
			slog.Error("error getting latest records from ninja. aborting...", "err", err)
			return
		}

		buildRequestWindows(res.Data)

		// get current elaborated data advancement

		// for each station / type

		// partition by date

		// func(station, type)

	})
}

type Elab struct {
	stationtypes []string
	where        string
}

func foo() {
	b := bdplib.FromEnv()

	n := odhts.NewCustomClient(env.NINJA_BASEURL, env.ODH_TOKEN_URL, "el-air-quality-rating")
	n.UseAuth(env.ODH_CLIENT_ID, env.ODH_CLIENT_SECRET)

	aggs := []Aggregation[odhts.StationDto[map[string]any], odhts.LatestDto]{}

	for _, agg := range aggs {
		// Get all the latest records from base and derived types
		req := odhts.DefaultRequest()
		req.Repr = odhts.TreeNode
		req.StationTypes = agg.stationtypes

		datatypes := map[string]struct{}{}
		periods := map[string]struct{}{}
		for _, dt := range append(agg.base, agg.derived...) {
			datatypes[dt.cname] = struct{}{}
			periods[strconv.Itoa(dt.period)] = struct{}{}
		}
		req.DataTypes = slices.Collect(maps.Keys(datatypes))
		periodsStr := strings.Join(slices.Collect(maps.Keys(periods)), ",")

		req.Limit = -1
		req.Select = agg.selectFields
		req.Where = fmt.Sprintf("sactive.eq.true,mperiod.in.(%s),%s", periodsStr, agg.filter)

		var res odhts.Response[NinjaTreeData]
		err := odhts.Latest(n, req, &res)
		if err != nil {
			slog.Error("error getting latest records from ninja. aborting...", "err", err)
			return
		}

		// Determine window per stationtype / station / type / period

		// For each
		// call handler function
		// populate bdp datamap and push it (either once or per station/slice)

	}

}

type Aggregation[Station any, Measure any] struct {
	stationtypes []string
	filter       string
	selectFields string
	base         []DataType
	derived      []DataType

	handle func(Station, []Measure) ([]Result, error)
}
type DataType struct {
	cname  string
	period int
}

type Result struct {
	Timestamp int64
	Period    uint64
	DataType  string
	Value     interface{}
}

func buildRequestWindows(dt NinjaTreeData) map[string]map[string]window {
	todos := make(map[string]map[string]window)
	for _, stations := range dt {
		for stationCode, station := range stations.Stations {
			for tname, dataType := range station.Datatypes {
				firstBase := minTime
				lastBase := minTime
				lastAggregate := minTime

				for _, m := range dataType.Measurements {

					if m.Period == uint64(basePeriod) {
						lastBase = m.Time.Time
						firstBase = m.Since.Time
					}
					if m.Period == periodAgg {
						lastAggregate = m.Time.Time
					}
				}

				// only consider stations that don't have up to date aggregates
				if lastBase.Sub(lastAggregate).Seconds() > periodAgg {
					if _, exists := todos[stationCode]; !exists {
						todos[stationCode] = make(map[string]window)
					}
					todos[stationCode][tname] = window{
						firstBase:     firstBase,
						lastBase:      lastBase,
						lastAggregate: lastAggregate,
					}
				}
			}
		}
	}
	return todos
}
