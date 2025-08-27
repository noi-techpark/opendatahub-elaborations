// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"context"
	"fmt"
	"log/slog"

	"github.com/noi-techpark/go-bdp-client/bdplib"
	"github.com/noi-techpark/go-timeseries-client/odhts"
	"github.com/noi-techpark/opendatahub-go-sdk/elab"
	"github.com/noi-techpark/opendatahub-go-sdk/ingest/ms"
	"github.com/noi-techpark/opendatahub-go-sdk/tel"
	"github.com/robfig/cron/v3"
)

var env struct {
	LOG_LEVEL          string
	CRON               string
	TS_API_BASEURL     string
	TS_API_REFERER     string
	AUTH_TOKEN_URL     string
	AUTH_CLIENT_ID     string
	AUTH_CLIENT_SECRET string
}

var EIAQ_NO2 = elab.ElaboratedDataType{Name: "EAQI-NO2", Description: "European Air Quality Index - NO2", Period: 3600, Rtype: "rating"}

func main() {
	ms.InitWithEnv(context.Background(), "", &env)
	slog.Info("Starting air-quality-rating elaboration...")
	defer tel.FlushOnPanic()

	b := bdplib.FromEnv()

	n := odhts.NewCustomClient(env.TS_API_BASEURL, env.AUTH_TOKEN_URL, env.TS_API_REFERER)
	n.UseAuth(env.AUTH_CLIENT_ID, env.AUTH_CLIENT_SECRET)

	e := elab.NewElaboration(&n, &b)
	e.StationTypes = []string{"EnvironmentStation"}
	e.BaseTypes = []elab.BaseDataType{
		{Name: "NO2-Alphasense_processed", Period: 3600},
		{Name: "NO2 - Ossidi di azoto", Period: 3600}}
	e.ElaboratedTypes = []elab.ElaboratedDataType{EIAQ_NO2}
	ms.FailOnError(context.Background(), e.SyncDataTypes(), "error syncing data types")

	c := cron.New(cron.WithSeconds())
	c.AddFunc(env.CRON, func() {
		is, err := e.RequestState()
		ms.FailOnError(context.Background(), err, "failed to get initial state")
		e.NewStationFollower().Elaborate(is, func(s elab.Station, ms []elab.Measurement) ([]elab.ElabResult, error) {
			ret := []elab.ElabResult{}
			for i, m := range ms {
				no2_um := *m.Value.Num
				no2_rating, err := rateNo2(no2_um, m)
				if err != nil {
					slog.Error("could not elaborate measurement. continuing", "measurement", m)
					continue
				}

				ret[i] = elab.ElabResult{
					Timestamp:   m.Timestamp.Time,
					Period:      elab.Period(m.Period),
					StationType: s.Stationtype,
					StationCode: s.Stationcode,
					DataType:    EIAQ_NO2.Name,
					Value:       no2_rating}
			}
			return ret, nil
		})
	})
}

func rateNo2(rating float64, m elab.Measurement) (string, error) {
	concentration := ""
	switch {
	case rating >= 340:
		concentration = "extremely poor"
	case rating >= 230:
		concentration = "very poor"
	case rating >= 120:
		concentration = "poor"
	case rating >= 90:
		concentration = "moderate"
	case rating >= 40:
		concentration = "fair"
	case rating >= 0:
		concentration = "good"
	default:
		return "", fmt.Errorf("invalid no2 value %f", rating)
	}
	return concentration, nil
}
