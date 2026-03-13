// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"context"
	"fmt"
	"log/slog"

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
}

var POLLUTANTS = []string{"NOx", "CO2"}

func main() {
	ms.InitWithEnv(context.Background(), "", &env)
	slog.Info("Starting traffic-a22-emissions-sum elaboration...")
	defer tel.FlushOnPanic()

	b := bdplib.FromEnv(env.BdpEnv)

	n := odhts.NewCustomClient(env.TS_API_BASE_URL, env.BDP_TOKEN_URL, env.TS_API_REFERER)
	n.UseAuth(env.BDP_CLIENT_ID, env.BDP_CLIENT_SECRET)

	pollutant := "NO2"

	e := elab.NewElaboration(&n, &b)
	e.StationTypes = []string{"TrafficSensor"}
	e.BaseTypes = []elab.BaseDataType{
		{Name: fmt.Sprintf("LIGHT_VEHICLE-%s-emissions", pollutant), Period: 600},
		{Name: fmt.Sprintf("HEAVY_VEHICLE-%s-emissions", pollutant), Period: 600},
		{Name: fmt.Sprintf("BUSES-%s-emissions", pollutant), Period: 600},
	}
	e.ElaboratedTypes = []elab.ElaboratedDataType{
		elab.ElaboratedDataType{Name: pollutant + "-emissions", Description: "emissions of " + pollutant, Period: 600, Rtype: "total", Unit: "g/km"},
		elab.ElaboratedDataType{Name: pollutant + "-emissions-impact", Description: "Impact of " + pollutant + " emissions", Period: 600, Rtype: "rating"},
	}
	e.Filter = where.In("sorigin", "A22")
	ms.FailOnError(context.Background(), e.SyncDataTypes(), "error syncing data types")

	job := func() {
		slog.Info("Starting elaboration run")
		is, err := e.RequestState()
		ms.FailOnError(context.Background(), err, "failed to get initial state")
		e.NewStationFollower()
	}

	job()
	c := cron.New(cron.WithSeconds())
	c.AddFunc(env.CRON, job)
	c.Start()
	select {}
}
