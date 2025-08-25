// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"context"
	"log/slog"

	"github.com/noi-techpark/go-bdp-client/bdplib"
	"github.com/noi-techpark/go-timeseries-client/odhts"
	"github.com/noi-techpark/go-timeseries-client/where"
	"github.com/noi-techpark/opendatahub-go-sdk/ingest/ms"
	"github.com/noi-techpark/opendatahub-go-sdk/tel"
	"github.com/robfig/cron/v3"
	"opendatahub.com/el-air-quality-rating/elab"
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

	e := elab.NewElaboration(&n, &b)
	e.StationTypes = []string{"ParkingStation", "ParkingSensor"}
	e.BaseTypes = []elab.BaseDataType{{Name: "occupied"}}
	e.ElaboratedTypes = []elab.ElaboratedDataType{{Name: "free", DontSync: true}}
	e.Filter = where.Gt("smetadata.capacity", "0")
	ms.FailOnError(context.Background(), e.SyncDataTypes(), "error syncing data types")

	c := cron.New(cron.WithSeconds())
	c.AddFunc(env.CRON, func() {
		is, err := e.GetInitialState()
		ms.FailOnError(context.Background(), err, "failed to get initial state")
		e.FollowStation(is, func(s elab.Station, ms []elab.Measurement) ([]elab.ElabResult, error) {
			capacity := s.Metadata["capacity"].(float64)
			ret := []elab.ElabResult{}
			for i, m := range ms {
				free := capacity - *m.Value.Num
				ret[i] = elab.ElabResult{Timestamp: m.Timestamp.Time, Period: elab.Period(m.Period), StationType: s.Stationtype, StationCode: s.Stationcode, DataType: "free", Value: free}
			}
			return ret, nil
		})
	})
}
