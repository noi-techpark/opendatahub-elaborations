// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"context"
	"fmt"
	"log/slog"
	"strings"
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
}

const (
	TRAFFIC_SENSOR = "TrafficSensor"
	origin         = "A22"
	emissionPeriod = uint64(600)
)

var POLLUTANTS = []string{"NOx", "CO2"}
var vehicleTypes = []string{"LIGHT_VEHICLES", "HEAVY_VEHICLES", "BUSES"}

// impactThresholds maps pollutant → [medium, high] threshold in g/km.
// These are placeholder values and should be calibrated against real data.
var impactThresholds = map[string][2]float64{
	"NOx": {500, 1500},
	"CO2": {5000, 15000},
}

func emissionsType(pollutant string) string { return pollutant + "-emissions" }

func main() {
	ms.InitWithEnv(context.Background(), "", &env)
	slog.Info("Starting traffic-a22-emissions-sum elaboration...")
	defer tel.FlushOnPanic()

	b := bdplib.FromEnv(env.BdpEnv)
	n := odhts.NewCustomClient(env.TS_API_BASE_URL, env.BDP_TOKEN_URL, env.TS_API_REFERER)
	n.UseAuth(env.BDP_CLIENT_ID, env.BDP_CLIENT_SECRET)

	// e.g. LIGHT_VEHICLE-CO2-emissions, HEAVY_VEHICLE-..., BUSES-...
	var baseTypes []elab.BaseDataType
	for _, p := range POLLUTANTS {
		for _, v := range vehicleTypes {
			baseTypes = append(baseTypes, elab.BaseDataType{
				Name:   fmt.Sprintf("%s-%s-emissions", v, p),
				Period: emissionPeriod,
			})
		}
	}
	var targetTypes []elab.ElaboratedDataType
	for _, p := range POLLUTANTS {
		targetTypes = append(targetTypes, elab.ElaboratedDataType{
			Name:        emissionsType(p),
			Description: "Combined " + p + " emissions across all vehicle types",
			Period:      emissionPeriod,
			Rtype:       "total",
			Unit:        "g/km",
		})
		targetTypes = append(targetTypes, elab.ElaboratedDataType{
			Name:        emissionsType(p) + "-impact",
			Description: "Impact of " + p + " emissions",
			Period:      emissionPeriod,
			Rtype:       "rating",
			Unit:        "",
		})
	}

	e := elab.NewElaboration(&n, &b)
	e.StationTypes = []string{TRAFFIC_SENSOR}
	e.BaseTypes = baseTypes
	e.ElaboratedTypes = targetTypes
	e.Filter = where.In("sorigin", origin)

	ms.FailOnError(context.Background(), e.SyncDataTypes(), "error syncing sensor data types")

	job := func() {
		slog.Info("Starting elaboration run")

		is, err := e.RequestState()
		ms.FailOnError(context.Background(), err, "failed to get sensor elaboration state")
		e.NewStationFollower().Elaborate(is, func(s elab.Station, ms []elab.Measurement) ([]elab.ElabResult, error) {
			sums := map[time.Time]map[string]elab.ElabResult{}
			for _, m := range ms {
				pollutant := strings.Split(m.TypeName, "-")[1]

				if sums[m.Timestamp.Time] == nil {
					sums[m.Timestamp.Time] = map[string]elab.ElabResult{}
				}
				var value float64 = 0
				if sums[m.Timestamp.Time][pollutant].Value != nil {
					value = sums[m.Timestamp.Time][pollutant].Value.(float64)
				}
				sums[m.Timestamp.Time][pollutant] = elab.ElabResult{
					Timestamp:   m.Timestamp.Time,
					Period:      emissionPeriod,
					StationType: s.Stationtype,
					StationCode: s.Stationcode,
					DataType:    emissionsType(pollutant),
					Value:       value + *m.Value.Num,
				}
			}
			results := []elab.ElabResult{}
			for _, tps := range sums {
				for _, r := range tps {
					pollutant := strings.Split(r.DataType, "-")[0]
					results = append(results, r)
					results = append(results, elab.ElabResult{
						Timestamp:   r.Timestamp,
						Period:      r.Period,
						StationType: r.StationType,
						StationCode: r.StationCode,
						Value:       rateEmissions(pollutant, r.Value.(float64)),
						DataType:    r.DataType + "-impact",
					})
				}
			}
			return results, nil
		})
		slog.Info("Elaboration run complete")
	}

	job()
	c := cron.New(cron.WithSeconds())
	c.AddFunc(env.CRON, job)
	c.Start()
	select {}
}

func rateEmissions(pollutant string, value float64) string {
	t, ok := impactThresholds[pollutant]
	if !ok {
		return "undefined"
	}
	switch {
	case value >= t[1]:
		return "high"
	case value >= t[0]:
		return "medium"
	default:
		return "low"
	}
}
