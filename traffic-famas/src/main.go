// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"context"
	"encoding/json"
	"log/slog"
	"os"
	"sync"
	"time"

	"github.com/noi-techpark/go-bdp-client/bdplib"
	"github.com/noi-techpark/go-timeseries-client/odhts"
	"github.com/noi-techpark/go-timeseries-client/where"
	"github.com/noi-techpark/opendatahub-go-sdk/elab"
	"github.com/noi-techpark/opendatahub-go-sdk/ingest/ms"
	"github.com/noi-techpark/opendatahub-go-sdk/tel"
	"github.com/robfig/cron/v3"
)

var env struct {
	bdplib.BdpEnv
	LOG_LEVEL       string
	CRON            string
	TS_API_BASE_URL string
	TS_API_REFERER  string
	// windows with fewer base records are not elaborated
	MIN_SAMPLES int `default:"6"`
	// optional RFC3339 start of the elaboration, used when no hourly data exists yet. Default is the beginning of time
	START_FROM string
	// if true, elaborate once but write nothing. Results are dumped as json to DRY_RUN_OUT (default stdout) and the program exits
	DRY_RUN     bool
	DRY_RUN_OUT string
}

const (
	TRAFFIC_SENSOR = "TrafficSensor"
	// origin of the data collected by traffic-famas-prov-bz
	origin = "FAMAS-traffic-provinceBZ"
	// FAMAS aggregation bucket
	basePeriod = uint64(300)
	// hourly
	targetPeriod = uint64(3600)
)

// Data types written by the traffic-famas-prov-bz transformer, with the way they are aggregated to hourly values.
// The elaborated data keeps the same type name, only the period differs.
// This is the convention of the other elaborations (e.g. environment-a22-averages, traffic-a22-data-quality)
//
// Counts are summed, speed/headway/gap are averaged. To change one, just change its aggregation name (see aggregations).
// Already written hourly records are not recomputed, so reset them if you change this on a running deployment.
var dataTypes = []struct{ name, aggregation string }{
	{"total-transits", "sum"},
	{"number-of-motorcycles", "sum"},
	{"number-of-cars", "sum"},
	{"number-of-cars-and-minivans-with-trailer", "sum"},
	{"number-of-small-trucks-and-vans", "sum"},
	{"number-of-medium-sized-trucks", "sum"},
	{"number-of-big-trucks", "sum"},
	{"number-of-articulated-trucks", "sum"},
	{"number-of-articulated-lorries", "sum"},
	{"number-of-busses", "sum"},
	{"number-of-unclassified-vehicles", "sum"},
	{"average-vehicle-speed", "avg"},
	{"headway", "avg"},
	{"headway-variance", "avg"},
	{"gap", "avg"},
	{"gap-variance", "avg"},
}

func main() {
	ms.InitWithEnv(context.Background(), "", &env)
	slog.Info("Starting traffic-famas elaboration...")
	defer tel.FlushOnPanic()

	aggs := map[string]Aggregation{}
	for _, t := range dataTypes {
		a, err := lookupAggregation(t.aggregation)
		ms.FailOnError(context.Background(), err, "invalid aggregation for "+t.name)
		aggs[t.name] = a
	}

	b := bdplib.FromEnv(env.BdpEnv)
	n := odhts.NewCustomClient(env.TS_API_BASE_URL, env.BDP_TOKEN_URL, env.TS_API_REFERER)
	n.UseAuth(env.BDP_CLIENT_ID, env.BDP_CLIENT_SECRET)

	var baseTypes []elab.BaseDataType
	var targetTypes []elab.ElaboratedDataType
	for _, dt := range dataTypes {
		t := dt.name
		baseTypes = append(baseTypes, elab.BaseDataType{Name: t, Period: basePeriod})
		targetTypes = append(targetTypes, elab.ElaboratedDataType{
			Name:   t,
			Period: targetPeriod,
			// The data type is owned (and described) by the collector. Syncing it here would overwrite its metadata
			DontSync: true,
		})
	}

	e := elab.NewElaboration(&n, &b)
	e.StationTypes = []string{TRAFFIC_SENSOR}
	e.BaseTypes = baseTypes
	e.ElaboratedTypes = targetTypes
	e.Filter = where.In("sorigin", origin)
	if env.START_FROM != "" {
		start, err := time.Parse(time.RFC3339, env.START_FROM)
		ms.FailOnError(context.Background(), err, "invalid START_FROM")
		e.StartingPoint = start
	}

	var dryMu sync.Mutex
	var dryResults []elab.ElabResult

	job := func() {
		slog.Info("Starting elaboration run")

		is, err := e.RequestState()
		ms.FailOnError(context.Background(), err, "failed to get sensor elaboration state")
		follower := e.NewStationFollower()
		follower.Elaborate(is, func(s elab.Station, ms []elab.Measurement) ([]elab.ElabResult, error) {
			res := aggregateStation(s, ms, aggs, env.MIN_SAMPLES)
			if env.DRY_RUN {
				// keep the results to ourselves, so the elaboration pushes nothing
				dryMu.Lock()
				dryResults = append(dryResults, res...)
				dryMu.Unlock()
				return nil, nil
			}
			return res, nil
		})
		slog.Info("Elaboration run complete")
	}

	job()
	if env.DRY_RUN {
		writeDryRun(env.DRY_RUN_OUT, dryResults)
		return
	}
	c := cron.New(cron.WithSeconds())
	c.AddFunc(env.CRON, job)
	c.Start()
	select {}
}

func writeDryRun(path string, results []elab.ElabResult) {
	out := os.Stdout
	if path != "" {
		f, err := os.Create(path)
		ms.FailOnError(context.Background(), err, "cannot create dry run output")
		defer f.Close()
		out = f
	}
	ms.FailOnError(context.Background(), json.NewEncoder(out).Encode(results), "cannot write dry run output")
	slog.Info("Dry run complete, nothing was written", "results", len(results))
}
