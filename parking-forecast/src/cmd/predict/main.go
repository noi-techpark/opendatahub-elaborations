// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

// Command predict performs the recursive 48h rollout across every station
// with a trained forest, then writes the legacy result.json (publishing to
// ODH/BDP is planned but not implemented yet). It replaces
// process4-prediction.py + process5-generate-json.py. Scheduled hourly as
// its own k8s CronJob.
//
// Unlike the old pipeline (one big matrix built once, in one CUTOFF_IX/park
// nested loop over a single joint model), this steps through the timeline
// one 5-minute tick at a time and, at each tick, evaluates every station's
// own forest — so a station's own lags and its neighbors' one-step-lagged
// occupancy naturally roll forward together without any circular
// dependency (see internal/features's package doc).
package main

import (
	"context"
	"log/slog"
	"time"

	"github.com/noi-techpark/opendatahub-go-sdk/ingest/ms"
	"github.com/noi-techpark/opendatahub-go-sdk/tel"

	"parking-forecast/internal/config"
	"parking-forecast/internal/features"
	"parking-forecast/internal/forest"
	"parking-forecast/internal/publish"
	"parking-forecast/internal/store"
)

// predictSafetyMargin accounts for ingest's cadence: by the time predict
// runs, the freshest occupancy sample might lag "now" by a bit. Stations
// whose actual last sample is still older than this get an all-null
// forecast (see readme-for-data-consumers.md: "this happens when a parking
// station has not sent up to date data"), same intent as before.
const predictSafetyMargin = 10 * time.Minute

// historyBuffer bounds how much history gets loaded per station: nothing
// beyond it is ever read once the rollout is running (same optimization
// process4-prediction.py made, for the same reason — lookups never reach
// further back than one week).
const historyBuffer = 8 * 24 * time.Hour

func main() {
	ctx := context.Background()

	var cfg config.Env
	ms.InitWithEnv(ctx, "", &cfg)
	defer tel.FlushOnPanic()

	db, err := store.Open(cfg.DbPath)
	ms.FailOnError(ctx, err, "opening store")
	defer db.Close()

	stations, err := db.ActiveStations()
	ms.FailOnError(ctx, err, "loading stations")
	slog.Info("prediction run starting", "stations", len(stations))

	neighborsByStation, err := db.AllNeighbors()
	ms.FailOnError(ctx, err, "loading neighbors")
	holidayMap, err := db.AllHolidays()
	ms.FailOnError(ctx, err, "loading holidays")
	weatherMap, err := db.AllWeather()
	ms.FailOnError(ctx, err, "loading weather")

	cutoff := time.Now().UTC().Add(-predictSafetyMargin).Truncate(features.StepSeconds * time.Second)
	horizonSteps := cfg.HoursToPredict * 60 / (features.StepSeconds / 60)
	from := cutoff.Add(-historyBuffer)
	to := cutoff.Add(time.Duration(horizonSteps) * features.StepSeconds * time.Second)

	slog.Info("forecast window", "cutoff", cutoff, "horizonSteps", horizonSteps, "to", to)

	rollout := newRollout(db, stations, neighborsByStation, holidayMap, weatherMap, from, cutoff, to, cfg)
	forecasts := rollout.run(horizonSteps, cfg)

	if err := publish.WriteResultJSON(cfg.ResultJsonPath, cutoff.Add(features.StepSeconds*time.Second), cfg.HoursToPredict, cfg.ModelVersion, forecasts); err != nil {
		slog.Error("writing legacy result.json failed", "err", err)
	} else {
		slog.Info("wrote legacy result.json", "path", cfg.ResultJsonPath)
	}

	slog.Info("prediction run complete")
}

type stationState struct {
	info      store.Station
	model     *forest.Forest
	neighbors []string
	occ       map[int64]float64 // grows with each predicted step
	mean7d    map[int64]float64 // precomputed once; see package doc for why that's safe
	failed    bool
}

type rollout struct {
	stations map[string]*stationState
	holidays map[string]store.DayInfo
	weather  map[string]int
	cutoff   time.Time
}

func newRollout(
	db *store.DB,
	stations []store.Station,
	neighborsByStation map[string][]string,
	holidayMap map[string]store.DayInfo,
	weatherMap map[string]int,
	from, cutoff, to time.Time,
	cfg config.Env,
) *rollout {
	r := &rollout{
		stations: map[string]*stationState{},
		holidays: holidayMap,
		weather:  weatherMap,
		cutoff:   cutoff,
	}

	models, err := loadModels(db, stations)
	if err != nil {
		slog.Error("loading models", "err", err)
	}

	for _, s := range stations {
		st := &stationState{info: s, neighbors: neighborsByStation[s.Scode]}

		model, ok := models[s.Scode]
		if !ok {
			st.failed = true // no trained model yet: forecast stays all-null
			r.stations[s.Scode] = st
			continue
		}
		st.model = model

		rawOcc, err := db.OccupancyMap(s.Scode, from, cutoff)
		if err != nil {
			slog.Error("loading occupancy history", "scode", s.Scode, "err", err)
			st.failed = true
			r.stations[s.Scode] = st
			continue
		}
		st.occ = features.Normalize(rawOcc, s.Capacity)
		st.mean7d = features.RollingMean7d(st.occ, cutoff, to)

		r.stations[s.Scode] = st
	}

	return r
}

func loadModels(db *store.DB, stations []store.Station) (map[string]*forest.Forest, error) {
	out := map[string]*forest.Forest{}
	for _, s := range stations {
		blob, _, ok, err := db.LoadModel(s.Scode)
		if err != nil {
			return out, err
		}
		if !ok {
			continue
		}
		f, err := forest.Unmarshal(blob)
		if err != nil {
			slog.Error("unmarshaling forest, skipping station", "scode", s.Scode, "err", err)
			continue
		}
		out[s.Scode] = f
	}
	return out, nil
}

// run steps through the forecast horizon one 5-minute tick at a time,
// predicting every still-viable station at each tick before moving to the
// next, so neighbor and lag features roll forward consistently.
func (r *rollout) run(horizonSteps int, cfg config.Env) []publish.StationForecast {
	forecasts := make(map[string]*publish.StationForecast, len(r.stations))
	for scode := range r.stations {
		forecasts[scode] = &publish.StationForecast{
			Scode:  scode,
			Points: make([]publish.Point, 0, horizonSteps),
		}
	}

	// cutoff itself (step 0) carries no forecast point; step 1 is cutoff+5min.
	cutoffUnix := r.cutoff.Unix()

	for step := 1; step <= horizonSteps; step++ {
		unix := cutoffUnix + int64(step)*features.StepSeconds
		ts := time.Unix(unix, 0).UTC()

		for scode, st := range r.stations {
			fc := forecasts[scode]
			if st.failed {
				fc.Points = append(fc.Points, publish.Point{TS: ts})
				continue
			}

			neighborVal, hasNeighbor := r.neighborMeanAt(st, unix-features.StepSeconds)
			neighborInput := map[int64]float64{}
			if hasNeighbor {
				neighborInput[unix-features.StepSeconds] = neighborVal
			}

			row, ok := features.Build(ts, features.Inputs{
				Occupancy: st.occ,
				Neighbor:  neighborInput,
				Mean7d:    st.mean7d,
				Holidays:  r.holidays,
				Weather:   r.weather,
			})
			if !ok {
				st.failed = true
				fc.Points = append(fc.Points, publish.Point{TS: ts})
				continue
			}

			meanRatio, loRatio, hiRatio := st.model.PredictStats(row[:], cfg.ForestLoPercentile, cfg.ForestHiPercentile)
			st.occ[unix] = meanRatio // feed the mean back in as the autoregressive "known" value for later steps

			capacity := st.info.Capacity
			lo := features.Denormalize(loRatio, capacity)
			mean := features.Denormalize(meanRatio, capacity)
			hi := features.Denormalize(hiRatio, capacity)
			fc.Points = append(fc.Points, publish.Point{TS: ts, Lo: &lo, Mean: &mean, Hi: &hi})
		}
	}

	out := make([]publish.StationForecast, 0, len(forecasts))
	for _, fc := range forecasts {
		out = append(out, *fc)
	}
	return out
}

func (r *rollout) neighborMeanAt(st *stationState, unix int64) (float64, bool) {
	sum, count := 0.0, 0
	for _, nc := range st.neighbors {
		neighbor, ok := r.stations[nc]
		if !ok || neighbor.occ == nil {
			continue
		}
		if v, ok := neighbor.occ[unix]; ok {
			sum += v
			count++
		}
	}
	if count == 0 {
		return 0, false
	}
	return sum / float64(count), true
}
