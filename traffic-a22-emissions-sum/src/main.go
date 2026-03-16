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
	TRAFFIC_SENSOR  = "TrafficSensor"
	TRAFFIC_STATION = "TrafficStation"
	origin          = "A22"
	emissionPeriod  = uint64(600)
)

var POLLUTANTS = []string{"NOx", "CO2"}
var vehicleTypes = []string{"LIGHT_VEHICLE", "HEAVY_VEHICLE", "BUSES"}

// impactThresholds maps pollutant → [medium, high] threshold in g/km.
// These are placeholder values and should be calibrated against real data.
var impactThresholds = map[string][2]float64{
	"NOx": {500, 1500},
	"CO2": {5000, 15000},
}

func emissionsType(pollutant string) string       { return pollutant + "-emissions" }
func emissionsImpactType(pollutant string) string { return pollutant + "-emissions-impact" }

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
	}

	e := elab.NewElaboration(&n, &b)
	e.StationTypes = []string{TRAFFIC_SENSOR, TRAFFIC_STATION}
	e.BaseTypes = baseTypes
	e.ElaboratedTypes = targetTypes
	e.Filter = where.In("sorigin", origin)

	ms.FailOnError(context.Background(), e.SyncDataTypes(), "error syncing sensor data types")

	job := func() {
		slog.Info("Starting elaboration run")

		es, err := e.RequestState()
		ms.FailOnError(context.Background(), err, "failed to get sensor elaboration state")
		sensorsByLoc := map[string][]elab.ESStation{}
		for scode, sensor := range es[TRAFFIC_SENSOR].Stations {
			par := sensorParentCode(scode)
			sensorsByLoc[par] = append(sensorsByLoc[par], sensor)
		}
		for locId, loc := range es[TRAFFIC_STATION].Stations {
			for _, p := range POLLUTANTS {
				start := loc.Datatypes[emissionsType(p)].Periods[emissionPeriod]
				if start.Before(e.StartingPoint) {
					start = e.StartingPoint
				}
				end := time.Time{}
				scodes := map[string]any{}
				for _, s := range sensorsByLoc[locId] {
					for tname, dt := range s.Datatypes {
						if strings.HasSuffix(tname, p+"-emissions") {
							scodes[s.Station.Stationcode] = struct{}{}
							dtEnd := dt.Periods[emissionPeriod]
							if dtEnd.After(end) {
								end = dtEnd
							}
						}
					}
				}
			}
		}
		slog.Info("Elaboration run complete")
	}

	job()
	c := cron.New(cron.WithSeconds())
	c.AddFunc(env.CRON, job)
	c.Start()
	select {}
}

type ElabPkg struct {
	pollutant string
	loc       elab.Station
	stations  []string
	start     time.Time
	end       time.Time
}

// sensorParentCode derives the TrafficStation code from a TrafficSensor code.
// Sensor format: "A22:<location>:<lane>" → Station format: "A22:<location>"
func sensorParentCode(sensorCode string) string {
	parts := strings.Split(sensorCode, ":")
	if len(parts) < 3 {
		return ""
	}
	return strings.Join(parts[:2], ":")
}
