// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

// Package features builds the fixed-size feature row the forest model is
// trained and evaluated on, shared by cmd/train and cmd/predict. Unlike the
// old pipeline, the feature count never grows with the number of stations
// (no one-hot station index) or with time resolution (no one-hot hour
// column) — this is what lets a single set of hyperparameters and a fast,
// independent per-station fit scale to many more stations.
package features

import (
	"math"
	"sort"
	"time"

	"parking-forecast/internal/store"
)

// Feature indices. Every row has exactly this many columns, in this order.
const (
	IdxSinTime = iota
	IdxCosTime
	IdxSinDow
	IdxCosDow
	IdxSinSeason
	IdxCosSeason
	IdxIsHoliday
	IdxIsSchool
	IdxWeather
	IdxLag5m
	IdxLag10m
	IdxLag1h
	IdxLag1d
	IdxLag1w
	IdxMean7d
	IdxNeighbor
	NumFeatures
)

const (
	StepSeconds = 300 // 5 minutes, matches the ODH parking occupancy sample period
	lag10m      = 2 * StepSeconds
	lag1h       = 12 * StepSeconds
	lag1d       = 288 * StepSeconds
	lag1w       = 2016 * StepSeconds
	mean7dSpan  = 7 * 24 * 60 * 60 // 7 days, in seconds
)

// Inputs bundles everything Build needs to read for one station. All maps
// are keyed by unix timestamp (UTC, 5-minute aligned) except Holidays/Weather
// which are keyed by ISO date (YYYY-MM-DD) — both train and predict populate
// these the same way, so the feature computation itself needs no special
// casing for the recursive multi-step forecast rollout (see cmd/predict).
type Inputs struct {
	// Occupancy ratio (occupancy/capacity) for this station.
	Occupancy map[int64]float64
	// Mean occupancy ratio across the station's neighbors, at the same
	// timestamps as Occupancy — see RollingMean7d/NeighborMeans for how to
	// build these two series efficiently.
	Neighbor map[int64]float64
	Mean7d   map[int64]float64
	Holidays map[string]store.DayInfo
	Weather  map[string]int
}

// Build constructs the feature row used to predict occupancy at ts. ok is
// false when mandatory data (a lag, the neighbor average, calendar or
// weather info) isn't available yet — the caller should skip this row
// (training) or treat the station as not-yet-forecastable at this point
// (prediction).
func Build(ts time.Time, in Inputs) (x [NumFeatures]float64, ok bool) {
	ts = ts.UTC()
	unix := ts.Unix()

	minuteOfDay := float64(ts.Hour()*60 + ts.Minute())
	angleDay := 2 * math.Pi * minuteOfDay / 1440
	x[IdxSinTime] = math.Sin(angleDay)
	x[IdxCosTime] = math.Cos(angleDay)

	angleWeek := 2 * math.Pi * float64(ts.Weekday()) / 7
	x[IdxSinDow] = math.Sin(angleWeek)
	x[IdxCosDow] = math.Cos(angleWeek)

	// Day-of-year, cyclical: the only way the model can learn annual
	// seasonality (tourist/ski season vs. off-season, etc.) at all — without
	// it, retaining more than a few weeks of history wouldn't teach the
	// model anything a shorter window doesn't already cover.
	angleYear := 2 * math.Pi * float64(ts.YearDay()-1) / 365.25
	x[IdxSinSeason] = math.Sin(angleYear)
	x[IdxCosSeason] = math.Cos(angleYear)

	date := ts.Format("2006-01-02")
	day, hasDay := in.Holidays[date]
	if !hasDay {
		return x, false
	}
	x[IdxIsHoliday] = boolToFloat(day.IsHoliday)
	x[IdxIsSchool] = boolToFloat(day.IsSchool)

	symbol, hasWeather := in.Weather[date]
	if !hasWeather {
		return x, false
	}
	x[IdxWeather] = float64(symbol)

	lag5mv, ok5 := in.Occupancy[unix-StepSeconds]
	lag10mv, ok10 := in.Occupancy[unix-lag10m]
	lag1hv, ok1h := in.Occupancy[unix-lag1h]
	lag1dv, ok1d := in.Occupancy[unix-lag1d]
	lag1wv, ok1w := in.Occupancy[unix-lag1w]
	if !ok5 || !ok10 || !ok1h || !ok1d || !ok1w {
		return x, false
	}
	x[IdxLag5m] = lag5mv
	x[IdxLag10m] = lag10mv
	x[IdxLag1h] = lag1hv
	x[IdxLag1d] = lag1dv
	x[IdxLag1w] = lag1wv

	mean7d, hasMean := in.Mean7d[unix]
	if !hasMean {
		return x, false
	}
	x[IdxMean7d] = mean7d

	neighbor, hasNeighbor := in.Neighbor[unix-StepSeconds]
	if !hasNeighbor {
		return x, false
	}
	x[IdxNeighbor] = neighbor

	return x, true
}

func boolToFloat(b bool) float64 {
	if b {
		return 1
	}
	return 0
}

// Normalize converts raw occupancy counts to ratios (occupancy/capacity) so
// that own-lag, neighbor and mean features are comparable across stations of
// different sizes. If capacity is unknown (<= 0), values pass through
// unchanged and the model effectively operates on raw counts for that
// station. Negative sensor readings are clamped to 0.
func Normalize(raw map[int64]float64, capacity float64) map[int64]float64 {
	out := make(map[int64]float64, len(raw))
	for ts, v := range raw {
		if v < 0 {
			v = 0
		}
		if capacity > 0 {
			v /= capacity
		}
		out[ts] = v
	}
	return out
}

// Denormalize converts a model prediction back to occupancy-count units,
// clamped to [0, capacity] when capacity is known.
func Denormalize(ratio, capacity float64) float64 {
	v := ratio
	if capacity > 0 {
		v *= capacity
		if v > capacity {
			v = capacity
		}
	}
	if v < 0 {
		v = 0
	}
	return v
}

// RollingMean7d computes, for every timestamp present in occ within
// [from, to], the mean of occ over the preceding 7 days ending at ts-5min
// (i.e. it never looks at ts itself, so it can't leak the training target
// and needs no special-casing during the predict rollout). Uses a
// sliding-window sum over the sorted timestamps, O(n log n), instead of
// recomputing a mean over ~2000 samples per row.
func RollingMean7d(occ map[int64]float64, from, to time.Time) map[int64]float64 {
	return rollingMean(occ, from, to, mean7dSpan)
}

func rollingMean(occ map[int64]float64, from, to time.Time, spanSeconds int64) map[int64]float64 {
	ts := make([]int64, 0, len(occ))
	for t := range occ {
		ts = append(ts, t)
	}
	sort.Slice(ts, func(i, j int) bool { return ts[i] < ts[j] })

	out := map[int64]float64{}
	sum := 0.0
	count := 0
	lo, hi := 0, 0 // window currently covers ts[lo:hi]

	fromUnix, toUnix := from.Unix(), to.Unix()
	for cur := fromUnix; cur <= toUnix; cur += StepSeconds {
		windowEnd := cur - StepSeconds   // inclusive upper bound (strictly before cur)
		windowStart := cur - spanSeconds // inclusive lower bound

		// include newly-eligible points ahead of the window
		for hi < len(ts) && ts[hi] <= windowEnd {
			sum += occ[ts[hi]]
			count++
			hi++
		}
		// drop points that have fallen out of the window behind it
		for lo < hi && ts[lo] < windowStart {
			sum -= occ[ts[lo]]
			count--
			lo++
		}

		if count > 0 {
			out[cur] = sum / float64(count)
		}
	}
	return out
}

// NeighborMeans computes, for every 5-minute grid point in [from, to], the
// mean occupancy ratio across a station's neighbors at that exact timestamp
// (Build itself applies the one-step lag when looking this up, to avoid a
// circular dependency between mutual neighbors during the predict rollout).
func NeighborMeans(neighborOcc []map[int64]float64, from, to time.Time) map[int64]float64 {
	out := map[int64]float64{}
	fromUnix, toUnix := from.Unix(), to.Unix()
	for cur := fromUnix; cur <= toUnix; cur += StepSeconds {
		sum, count := 0.0, 0
		for _, occ := range neighborOcc {
			if v, ok := occ[cur]; ok {
				sum += v
				count++
			}
		}
		if count > 0 {
			out[cur] = sum / float64(count)
		}
	}
	return out
}
