// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"context"
	"fmt"
	"log/slog"
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
	LOG_LEVEL         string
	CRON              string
	TS_API_BASE_URL   string
	TS_API_REFERER    string
	ODH_TOKEN_URL     string
	ODH_CLIENT_ID     string
	ODH_CLIENT_SECRET string
}

var OCCUPIED = "occupied"
var FREE = "free"
var STATIONTYPES = []string{"ParkingStation", "ParkingSensor"}

func main() {
	ms.InitWithEnv(context.Background(), "", &env)
	slog.Info("Starting parking-free-slot-calculation elaboration...")
	defer tel.FlushOnPanic()

	b := bdplib.FromEnv()

	n := odhts.NewCustomClient(env.TS_API_BASE_URL, env.ODH_TOKEN_URL, env.TS_API_REFERER)
	n.UseAuth(env.ODH_CLIENT_ID, env.ODH_CLIENT_SECRET)

	// master elaboration to sync data once at startup, commented out because no types are to sync
	// e := elab.NewElaboration(&n, &b)
	// e.StationTypes = STATIONTYPES
	// e.BaseTypes = []elab.BaseDataType{
	// 	{Name: OCCUPIED},
	// }
	// e.ElaboratedTypes = []elab.ElaboratedDataType{
	// 	{Name: FREE, DontSync: true},
	// }
	// ms.FailOnError(context.Background(), e.SyncDataTypes(), "error syncing data types")

	job := func() {
		slog.Info("Starting elaboration run")
		stationTrack := sync.Map{}
		seenPeriods, err := getDistinctPeriods(n)
		if err != nil {
			slog.Error("error getting periods from ninja. aborting...", "err", err)
			panic(err)
		}

		//////////////////////////////////////
		wg := sync.WaitGroup{}

		for p := range seenPeriods {
			// // Occupied -> Free
			wg.Add(1)
			go func(period int64) {
				defer func() { wg.Done() }()

				e := elab.NewElaboration(&n, &b)
				e.StationTypes = STATIONTYPES
				e.BaseTypes = []elab.BaseDataType{
					{Name: OCCUPIED, Period: elab.Period(period)},
				}
				e.ElaboratedTypes = []elab.ElaboratedDataType{
					{Name: FREE, Period: elab.Period(period), DontSync: true},
				}

				is, err := e.RequestState()
				ms.FailOnError(context.Background(), err, "failed to get initial state")
				e.NewWideTypeFollower(time.Duration(30*24)*time.Hour).Elaborate(is,
					func(t elab.BaseDataType, from time.Time, to time.Time, s elab.Station, ms []elab.Measurement) ([]elab.ElabResult, error) {
						stationTrack.Store(s.Stationcode, nil)
						return handlerOccupiedToFree(from, to, s, ms)
					})
			}(p)

			// Free -> Occupied
			wg.Add(1)
			go func(period int64) {
				defer func() { wg.Done() }()

				e := elab.NewElaboration(&n, &b)
				e.StationTypes = STATIONTYPES
				e.BaseTypes = []elab.BaseDataType{
					{Name: FREE, Period: elab.Period(period)},
				}
				e.ElaboratedTypes = []elab.ElaboratedDataType{
					{Name: OCCUPIED, Period: elab.Period(period), DontSync: true},
				}

				is, err := e.RequestState()
				ms.FailOnError(context.Background(), err, "failed to get initial state")
				e.NewWideTypeFollower(time.Duration(30*24)*time.Hour).Elaborate(is,
					func(t elab.BaseDataType, from time.Time, to time.Time, s elab.Station, ms []elab.Measurement) ([]elab.ElabResult, error) {
						stationTrack.Store(s.Stationcode, nil)
						return handlerFreeToOccupied(from, to, s, ms)
					})
			}(p)
		}

		wg.Wait()

		count := 0
		stationTrack.Range(func(key, value any) bool {
			count++
			return true
		})
		slog.Info("Elaboration job complete", "stationsCount", count)
	}

	job()
	c := cron.New(cron.WithSeconds())
	c.AddFunc(env.CRON, job)
	c.Start()
	select {}
}

func getDistinctPeriods(tsClient odhts.C) (map[int64]any, error) {
	seenPeriods := map[int64]any{}

	type DtoLatestPeriodData = []struct {
		Period int64 `json:"mperiod"`
	}

	req := odhts.DefaultRequest()
	req.Repr = odhts.FlatNode
	req.Distinct = true
	req.DataTypes = []string{OCCUPIED, FREE}
	req.StationTypes = STATIONTYPES
	req.Where = where.Eq("sactive", "true")
	req.Select = "mperiod"

	var res odhts.Response[DtoLatestPeriodData]
	err := odhts.Latest(tsClient, req, &res)
	if err != nil {
		return nil, err
	}

	for _, p := range res.Data {
		if _, ok := seenPeriods[p.Period]; !ok {
			seenPeriods[p.Period] = nil
		}
	}
	return seenPeriods, nil
}

func handlerOccupiedToFree(from time.Time, to time.Time, s elab.Station, ms []elab.Measurement) ([]elab.ElabResult, error) {
	slog.Debug("<occupied-free> Elaborating station", "from", from, "to", to, "station", s, "rec_cnt", len(ms))
	ret := make([]elab.ElabResult, len(ms))
	capacity := float64(1)
	if s.Stationtype == "ParkingStation" {
		c, ok := s.Metadata["capacity"]
		if !ok {
			return nil, fmt.Errorf("missing capacity field")
		}
		capacity, ok = c.(float64)
		if !ok {
			return nil, fmt.Errorf("capacity field has non-number type")
		}
	}

	if capacity <= 0 {
		return nil, fmt.Errorf("zero or negative capacity")
	}

	for i, m := range ms {
		value := int(capacity - *m.Value.Num)
		if value < 0 {
			slog.Warn("<occupied-free> zero or negative free value", "stationcode", s.Stationcode, "stationtype", s.Stationtype, "capacity", capacity, "meas", m)
			value = 0
		}
		ret[i] = elab.ElabResult{
			Timestamp:   m.Timestamp.Time,
			Period:      elab.Period(m.Period),
			StationType: s.Stationtype,
			StationCode: s.Stationcode,
			DataType:    FREE,
			Value:       value}
	}
	return ret, nil
}

func handlerFreeToOccupied(from time.Time, to time.Time, s elab.Station, ms []elab.Measurement) ([]elab.ElabResult, error) {
	slog.Debug("<free-occupied> Elaborating station", "from", from, "to", to, "station", s, "rec_cnt", len(ms))
	ret := make([]elab.ElabResult, len(ms))
	capacity := float64(1)
	if s.Stationtype == "ParkingStation" {
		c, ok := s.Metadata["capacity"]
		if !ok {
			return nil, fmt.Errorf("missing capacity field")
		}
		capacity, ok = c.(float64)
		if !ok {
			return nil, fmt.Errorf("capacity field has non-number type")
		}
	}

	if capacity <= 0 {
		return nil, fmt.Errorf("zero or negative capacity")
	}

	for i, m := range ms {
		value := int(capacity - *m.Value.Num)
		if value < 0 {
			slog.Warn("<free-occupied> zero or negative free value", "stationcode", s.Stationcode, "stationtype", s.Stationtype, "capacity", capacity, "meas", m)
			value = 0
		}
		ret[i] = elab.ElabResult{
			Timestamp:   m.Timestamp.Time,
			Period:      elab.Period(m.Period),
			StationType: s.Stationtype,
			StationCode: s.Stationcode,
			DataType:    FREE,
			Value:       value}
	}
	return ret, nil
}
