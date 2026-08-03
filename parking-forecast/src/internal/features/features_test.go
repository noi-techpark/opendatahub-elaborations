// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package features

import (
	"math"
	"testing"
	"time"

	"parking-forecast/internal/store"
)

func TestSeasonalFeatureWrapsAroundNewYear(t *testing.T) {
	full := func(ts time.Time) Inputs {
		unix := ts.Unix()
		return Inputs{
			Occupancy: map[int64]float64{
				unix - StepSeconds: 0.1, unix - lag10m: 0.1, unix - lag1h: 0.1,
				unix - lag1d: 0.1, unix - lag1w: 0.1,
			},
			Neighbor: map[int64]float64{unix - StepSeconds: 0.2},
			Mean7d:   map[int64]float64{unix: 0.3},
			Holidays: map[string]store.DayInfo{ts.Format("2006-01-02"): {}},
			Weather:  map[string]int{ts.Format("2006-01-02"): 1},
		}
	}

	dec31 := time.Date(2025, 12, 31, 12, 0, 0, 0, time.UTC)
	jan1 := time.Date(2026, 1, 1, 12, 0, 0, 0, time.UTC)
	jul1 := time.Date(2026, 7, 1, 12, 0, 0, 0, time.UTC)

	xDec31, ok := Build(dec31, full(dec31))
	if !ok {
		t.Fatalf("expected ok=true for dec31")
	}
	xJan1, ok := Build(jan1, full(jan1))
	if !ok {
		t.Fatalf("expected ok=true for jan1")
	}
	xJul1, ok := Build(jul1, full(jul1))
	if !ok {
		t.Fatalf("expected ok=true for jul1")
	}

	distNewYear := math.Hypot(xDec31[IdxSinSeason]-xJan1[IdxSinSeason], xDec31[IdxCosSeason]-xJan1[IdxCosSeason])
	distHalfYear := math.Hypot(xDec31[IdxSinSeason]-xJul1[IdxSinSeason], xDec31[IdxCosSeason]-xJul1[IdxCosSeason])

	if distNewYear >= distHalfYear {
		t.Fatalf("Dec 31 should be much closer to Jan 1 than to Jul 1 in season space: distNewYear=%v distHalfYear=%v", distNewYear, distHalfYear)
	}
	if distNewYear > 0.1 {
		t.Fatalf("Dec 31 / Jan 1 should be nearly identical in season space, got distance %v", distNewYear)
	}
}

func TestRollingMean7dExcludesCurrentPoint(t *testing.T) {
	base := time.Date(2026, 1, 8, 12, 0, 0, 0, time.UTC) // an arbitrary Thursday noon
	occ := map[int64]float64{}
	// constant 0.5 for the whole week before base, then a spike exactly at base
	for t := base.Add(-8 * 24 * time.Hour); !t.After(base); t = t.Add(StepSeconds * time.Second) {
		occ[t.Unix()] = 0.5
	}
	occ[base.Unix()] = 999 // must NOT leak into its own rolling mean

	out := RollingMean7d(occ, base.Add(-1*time.Hour), base)
	got, ok := out[base.Unix()]
	if !ok {
		t.Fatalf("expected a value at base ts")
	}
	if math.Abs(got-0.5) > 1e-9 {
		t.Fatalf("rolling mean at base = %v, want ~0.5 (must not include the current point)", got)
	}
}

func TestRollingMean7dMissingWhenNoHistory(t *testing.T) {
	base := time.Date(2026, 1, 8, 12, 0, 0, 0, time.UTC)
	occ := map[int64]float64{base.Unix(): 1.0}
	out := RollingMean7d(occ, base, base)
	if _, ok := out[base.Unix()]; ok {
		t.Fatalf("expected no rolling mean when there's no preceding history")
	}
}

func TestBuildRequiresAllMandatoryInputs(t *testing.T) {
	ts := time.Date(2026, 1, 8, 8, 5, 0, 0, time.UTC)
	unix := ts.Unix()

	full := Inputs{
		Occupancy: map[int64]float64{
			unix - StepSeconds: 0.1,
			unix - lag10m:      0.1,
			unix - lag1h:       0.1,
			unix - lag1d:       0.1,
			unix - lag1w:       0.1,
		},
		Neighbor: map[int64]float64{unix - StepSeconds: 0.2},
		Mean7d:   map[int64]float64{unix: 0.3},
		Holidays: map[string]store.DayInfo{"2026-01-08": {IsSchool: true}},
		Weather:  map[string]int{"2026-01-08": 5},
	}

	if _, ok := Build(ts, full); !ok {
		t.Fatalf("expected ok=true when all mandatory inputs are present")
	}

	missingLag := full
	missingLag.Occupancy = map[int64]float64{unix - StepSeconds: 0.1} // missing the rest
	if _, ok := Build(ts, missingLag); ok {
		t.Fatalf("expected ok=false when a lag is missing")
	}

	missingNeighbor := full
	missingNeighbor.Neighbor = map[int64]float64{}
	if _, ok := Build(ts, missingNeighbor); ok {
		t.Fatalf("expected ok=false when the neighbor average is missing")
	}

	missingWeather := full
	missingWeather.Weather = map[string]int{}
	if _, ok := Build(ts, missingWeather); ok {
		t.Fatalf("expected ok=false when weather is missing")
	}
}

func TestNeighborMeansAveragesAvailableNeighbors(t *testing.T) {
	base := time.Date(2026, 1, 8, 12, 0, 0, 0, time.UTC)
	n1 := map[int64]float64{base.Unix(): 0.2}
	n2 := map[int64]float64{base.Unix(): 0.6}
	out := NeighborMeans([]map[int64]float64{n1, n2}, base, base)
	if math.Abs(out[base.Unix()]-0.4) > 1e-9 {
		t.Fatalf("got %v, want 0.4", out[base.Unix()])
	}
}
