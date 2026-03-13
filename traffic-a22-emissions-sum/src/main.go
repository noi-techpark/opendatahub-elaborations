// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"context"
	"fmt"
	"log/slog"
	"strings"
	"sync/atomic"
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
	stTypeSensor   = "TrafficSensor"
	stTypeStation  = "TrafficStation"
	origin         = "A22"
	emissionPeriod = uint64(600)
)

var POLLUTANTS = []string{"NOx", "CO2"}
var vehicleTypes = []string{"LIGHT_VEHICLE", "HEAVY_VEHICLE", "BUSES"}

// impactThresholds maps pollutant → [medium, high] threshold in g/km.
// These are placeholder values and should be calibrated against real data.
var impactThresholds = map[string][2]float64{
	"NOx": {500, 1500},
	"CO2": {5000, 15000},
}

func emissionsType(pollutant string) string      { return pollutant + "-emissions" }
func emissionsImpactType(pollutant string) string { return pollutant + "-emissions-impact" }
func vehicleEmissionsType(vehicle, pollutant string) string {
	return fmt.Sprintf("%s-%s-emissions", vehicle, pollutant)
}

func main() {
	ms.InitWithEnv(context.Background(), "", &env)
	slog.Info("Starting traffic-a22-emissions-sum elaboration...")
	defer tel.FlushOnPanic()

	b := bdplib.FromEnv(env.BdpEnv)
	n := odhts.NewCustomClient(env.TS_API_BASE_URL, env.BDP_TOKEN_URL, env.TS_API_REFERER)
	n.UseAuth(env.BDP_CLIENT_ID, env.BDP_CLIENT_SECRET)

	// ------------------------------------------------------------------
	// Phase 1: sensor-level elaboration
	// Base:       LIGHT_VEHICLE-{poll}-emissions, HEAVY_VEHICLE-..., BUSES-...
	// Elaborated: {poll}-emissions  (on TrafficSensor)
	// ------------------------------------------------------------------
	var sensorBaseTypes []elab.BaseDataType
	for _, p := range POLLUTANTS {
		for _, v := range vehicleTypes {
			sensorBaseTypes = append(sensorBaseTypes, elab.BaseDataType{
				Name:   vehicleEmissionsType(v, p),
				Period: emissionPeriod,
			})
		}
	}

	e1 := elab.NewElaboration(&n, &b)
	e1.StationTypes = []string{stTypeSensor}
	e1.BaseTypes = sensorBaseTypes
	for _, p := range POLLUTANTS {
		e1.ElaboratedTypes = append(e1.ElaboratedTypes, elab.ElaboratedDataType{
			Name:        emissionsType(p),
			Description: "Combined " + p + " emissions across all vehicle types",
			Period:      emissionPeriod,
			Rtype:       "total",
			Unit:        "g/km",
		})
	}
	e1.Filter = where.In("sorigin", origin)

	// ------------------------------------------------------------------
	// Phase 2: station-level elaboration
	// Base:       {poll}-emissions  (on TrafficSensor, produced by Phase 1)
	// Elaborated: {poll}-emissions + {poll}-emissions-impact  (on TrafficStation)
	// ------------------------------------------------------------------
	var stationBaseTypes []elab.BaseDataType
	for _, p := range POLLUTANTS {
		stationBaseTypes = append(stationBaseTypes, elab.BaseDataType{
			Name:   emissionsType(p),
			Period: emissionPeriod,
		})
	}

	e2 := elab.NewElaboration(&n, &b)
	// Query both types so RequestState captures sensor "to" and station "from" in one call
	e2.StationTypes = []string{stTypeSensor, stTypeStation}
	e2.BaseTypes = stationBaseTypes
	for _, p := range POLLUTANTS {
		e2.ElaboratedTypes = append(e2.ElaboratedTypes, elab.ElaboratedDataType{
			Name:     emissionsType(p),
			DontSync: true, // already synced by e1
		})
		e2.ElaboratedTypes = append(e2.ElaboratedTypes, elab.ElaboratedDataType{
			Name:        emissionsImpactType(p),
			Description: "Emissions impact rating for " + p,
			Period:      emissionPeriod,
			Rtype:       "rating",
		})
	}
	e2.Filter = where.In("sorigin", origin)

	ms.FailOnError(context.Background(), e1.SyncDataTypes(), "error syncing sensor data types")
	ms.FailOnError(context.Background(), e2.SyncDataTypes(), "error syncing station data types")

	job := func() {
		slog.Info("Starting elaboration run")

		// Phase 1: sum vehicle-type emissions → per-pollutant sensor emissions
		is1, err := e1.RequestState()
		ms.FailOnError(context.Background(), err, "failed to get sensor elaboration state")
		cnt := atomic.Int32{}
		e1.NewStationFollower().Elaborate(is1, func(s elab.Station, measurements []elab.Measurement) ([]elab.ElabResult, error) {
			cnt.Add(1)
			return elaborateSensor(s, measurements)
		})
		slog.Info("Sensor elaboration complete", "stations", cnt.Load())

		// Phase 2: sum sensor emissions to station level, compute impact ratings
		is2, err := e2.RequestState()
		ms.FailOnError(context.Background(), err, "failed to get station elaboration state")
		if err := elaborateStations(e2, is2); err != nil {
			slog.Error("Station elaboration failed", "err", err)
		}

		slog.Info("Elaboration run complete")
	}

	job()
	c := cron.New(cron.WithSeconds())
	c.AddFunc(env.CRON, job)
	c.Start()
	select {}
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

// elaborateSensor sums vehicle-type-specific emissions into combined per-pollutant emissions
// for a single TrafficSensor station.
func elaborateSensor(s elab.Station, measurements []elab.Measurement) ([]elab.ElabResult, error) {
	type key struct {
		pollutant string
		ts        time.Time
	}
	sums := map[key]float64{}

	for _, m := range measurements {
		if m.Value.Num == nil {
			continue
		}
		for _, p := range POLLUTANTS {
			// Type name pattern: "{VEHICLE_TYPE}-{pollutant}-emissions"
			if strings.Contains(m.TypeName, "-"+p+"-") {
				sums[key{p, m.Timestamp.Time}] += *m.Value.Num
				break
			}
		}
	}

	results := make([]elab.ElabResult, 0, len(sums))
	for k, sum := range sums {
		results = append(results, elab.ElabResult{
			Timestamp:   k.ts,
			Period:      emissionPeriod,
			StationType: stTypeSensor,
			StationCode: s.Stationcode,
			DataType:    emissionsType(k.pollutant),
			Value:       sum,
		})
	}
	return results, nil
}

// elaborateStations sums sensor-level emissions to TrafficStation level and
// computes impact ratings for each station.
func elaborateStations(e elab.Elaboration, is elab.ElaborationState) error {
	sensorState := is[stTypeSensor]
	stationState := is[stTypeStation]

	if len(sensorState.Stations) == 0 {
		slog.Info("No sensor data available for station elaboration")
		return nil
	}

	// Build map: station code → child sensor codes
	stationSensors := map[string][]string{}
	for sensorCode := range sensorState.Stations {
		if stCode := sensorParentCode(sensorCode); stCode != "" {
			stationSensors[stCode] = append(stationSensors[stCode], sensorCode)
		}
	}

	var allResults []elab.ElabResult

	for stCode, sensorCodes := range stationSensors {
		for _, pollutant := range POLLUTANTS {
			elabType := emissionsType(pollutant)

			// from: latest station-level {poll}-emissions (where we left off last run)
			from := e.StartingPoint
			if stSt, ok := stationState.Stations[stCode]; ok {
				if dt, ok := stSt.Datatypes[elabType]; ok {
					if t, ok := dt.Periods[emissionPeriod]; ok && !t.IsZero() {
						from = t
					}
				}
			}

			// to: latest sensor-level {poll}-emissions across all child sensors
			var to time.Time
			for _, sensorCode := range sensorCodes {
				sensor := sensorState.Stations[sensorCode]
				if dt, ok := sensor.Datatypes[elabType]; ok {
					if t, ok := dt.Periods[emissionPeriod]; ok && t.After(to) {
						to = t
					}
				}
			}

			if !to.After(from) {
				slog.Debug("Station up-to-date", "station", stCode, "pollutant", pollutant)
				continue
			}

			// Fetch sensor emissions history for the catch-up window [from, to]
			history, err := e.RequestHistory(
				[]string{stTypeSensor},
				sensorCodes,
				[]string{elabType},
				[]elab.Period{emissionPeriod},
				from,
				to.Add(time.Millisecond),
			)
			if err != nil {
				slog.Error("Failed to fetch history", "station", stCode, "pollutant", pollutant, "err", err)
				continue
			}

			// Sum across sensors for each timestamp
			tsSums := map[time.Time]float64{}
			for _, m := range history {
				if m.Value.Num != nil {
					tsSums[m.Timestamp.Time] += *m.Value.Num
				}
			}

			for ts, sum := range tsSums {
				allResults = append(allResults, elab.ElabResult{
					Timestamp:   ts,
					Period:      emissionPeriod,
					StationType: stTypeStation,
					StationCode: stCode,
					DataType:    elabType,
					Value:       sum,
				})
				allResults = append(allResults, elab.ElabResult{
					Timestamp:   ts,
					Period:      emissionPeriod,
					StationType: stTypeStation,
					StationCode: stCode,
					DataType:    emissionsImpactType(pollutant),
					Value:       rateEmissionsImpact(pollutant, sum),
				})
			}
		}
	}

	return e.PushResults(stTypeStation, allResults)
}

// rateEmissionsImpact returns a low/medium/high rating for a given pollutant value (g/km).
func rateEmissionsImpact(pollutant string, value float64) string {
	t, ok := impactThresholds[pollutant]
	if !ok {
		return "low"
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
