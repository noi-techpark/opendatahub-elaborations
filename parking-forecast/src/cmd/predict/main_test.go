// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"testing"
	"time"

	"parking-forecast/internal/config"
	"parking-forecast/internal/features"
	"parking-forecast/internal/forest"
	"parking-forecast/internal/publish"
	"parking-forecast/internal/store"
)

// constantForest builds a forest that (approximately) always predicts value,
// regardless of input — enough to exercise the rollout's bookkeeping without
// depending on forest.Fit's split-selection behavior.
func constantForest(t *testing.T, value float64) *forest.Forest {
	t.Helper()
	X := make([][]float64, 20)
	y := make([]float64, 20)
	for i := range X {
		X[i] = make([]float64, features.NumFeatures)
		y[i] = value
	}
	cfg := forest.DefaultConfig()
	cfg.NumTrees = 3
	cfg.MinLeafSamples = 1
	return forest.Fit(X, y, cfg)
}

func TestRolloutProducesFullHorizonAndHandlesMissingModel(t *testing.T) {
	now := time.Date(2026, 1, 8, 12, 0, 0, 0, time.UTC)
	const horizonSteps = 12 // 1 hour at 5-minute steps

	to := now.Add(time.Duration(horizonSteps) * features.StepSeconds * time.Second)

	holidays := map[string]store.DayInfo{}
	weather := map[string]int{}
	for d := now.AddDate(0, 0, -10); !d.After(now.AddDate(0, 0, 3)); d = d.AddDate(0, 0, 1) {
		key := d.Format("2006-01-02")
		holidays[key] = store.DayInfo{IsSchool: true}
		weather[key] = 1
	}

	// seed 8 days of history so lag1w/mean7d are always satisfiable
	occA := map[int64]float64{}
	occB := map[int64]float64{}
	for ts := now.Add(-8 * 24 * time.Hour); !ts.After(now); ts = ts.Add(features.StepSeconds * time.Second) {
		occA[ts.Unix()] = 0.3
		occB[ts.Unix()] = 0.5
	}

	r := &rollout{
		stations: map[string]*stationState{
			"A": {
				info:      store.Station{Scode: "A", StationType: "ParkingStation", Capacity: 100},
				neighbors: []string{"B"},
				occ:       occA,
				model:     constantForest(t, 0.4),
				mean7d:    features.RollingMean7d(occA, now, to),
			},
			"B": {
				info:      store.Station{Scode: "B", StationType: "ParkingStation", Capacity: 50},
				neighbors: []string{"A"},
				occ:       occB,
				model:     constantForest(t, 0.4),
				mean7d:    features.RollingMean7d(occB, now, to),
			},
			"C": {
				info:   store.Station{Scode: "C", StationType: "ParkingStation", Capacity: 10},
				failed: true, // no trained model
			},
		},
		holidays: holidays,
		weather:  weather,
		cutoff:   now,
	}

	cfg := config.Env{ForestLoPercentile: 0.1, ForestHiPercentile: 0.9}
	forecasts := r.run(horizonSteps, cfg)

	byScode := map[string]publish.StationForecast{}
	for _, f := range forecasts {
		byScode[f.Scode] = f
	}

	for _, scode := range []string{"A", "B", "C"} {
		if len(byScode[scode].Points) != horizonSteps {
			t.Fatalf("%s: got %d points, want %d", scode, len(byScode[scode].Points), horizonSteps)
		}
	}

	for _, p := range byScode["A"].Points {
		if p.Mean == nil {
			t.Fatalf("A: expected a non-null forecast (has model + history)")
		}
		if *p.Mean < 0 || *p.Mean > 100 {
			t.Fatalf("A: forecast %v outside [0, capacity]", *p.Mean)
		}
		if p.Lo == nil || p.Hi == nil || *p.Lo > *p.Mean || *p.Hi < *p.Mean {
			t.Fatalf("A: lo/mean/hi out of order: %v/%v/%v", *p.Lo, *p.Mean, *p.Hi)
		}
	}

	for _, p := range byScode["C"].Points {
		if p.Mean != nil || p.Lo != nil || p.Hi != nil {
			t.Fatalf("C: expected an all-null forecast (no trained model), got %+v", p)
		}
	}
}
