// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package publish

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"path/filepath"
	"time"
)

// resultJSON mirrors the schema documented in readme-for-data-consumers.md
// (schema_version "1.1"); model_version is bumped to reflect the new model,
// the rest of the shape is unchanged so existing consumers keep working.
type resultJSON struct {
	PublishTimestamp       string                 `json:"publish_timestamp"`
	ForecastStartTimestamp string                 `json:"forecast_start_timestamp"`
	ForecastPeriodSeconds  int                    `json:"forecast_period_seconds"`
	ForecastDurationHours  int                    `json:"forecast_duration_hours"`
	ModelVersion           string                 `json:"model_version"`
	SchemaVersion          string                 `json:"schema_version"`
	Timeseries             map[string][]pointJSON `json:"timeseries"`
}

type pointJSON struct {
	TS   string   `json:"ts"`
	Lo   *float64 `json:"lo"`
	Mean *float64 `json:"mean"`
	Hi   *float64 `json:"hi"`
	// RMSE was already disabled upstream of this rewrite (see rmse.py /
	// readme-for-data-consumers.md); kept in the schema, always null.
	RMSE *float64 `json:"rmse"`
}

// WriteResultJSON renders forecasts in the legacy schema to path, creating
// parent directories as needed.
func WriteResultJSON(path string, forecastStart time.Time, hoursToPredict int, modelVersion string, forecasts []StationForecast) error {
	doc := resultJSON{
		PublishTimestamp:       pyDatetimeStr(time.Now().UTC(), true),
		ForecastStartTimestamp: pyDatetimeStr(forecastStart.UTC(), false),
		ForecastPeriodSeconds:  300,
		ForecastDurationHours:  hoursToPredict,
		ModelVersion:           modelVersion,
		SchemaVersion:          "1.1",
		Timeseries:             map[string][]pointJSON{},
	}

	for _, sf := range forecasts {
		points := make([]pointJSON, 0, len(sf.Points))
		for _, p := range sf.Points {
			points = append(points, pointJSON{
				TS:   pyDatetimeStr(p.TS.UTC(), false),
				Lo:   round1(p.Lo),
				Mean: round1(p.Mean),
				Hi:   round1(p.Hi),
				RMSE: nil,
			})
		}
		doc.Timeseries[sf.Scode] = points
	}

	if dir := filepath.Dir(path); dir != "." {
		if err := os.MkdirAll(dir, 0o755); err != nil {
			return fmt.Errorf("creating result directory: %w", err)
		}
	}

	f, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("creating %s: %w", path, err)
	}
	defer f.Close()

	return json.NewEncoder(f).Encode(doc)
}

func round1(v *float64) *float64 {
	if v == nil {
		return nil
	}
	r := math.Round(*v*10) / 10
	return &r
}

// pyDatetimeStr formats t the way Python's str(datetime) does for a
// timezone-aware UTC datetime, e.g. "2026-01-08 10:05:00+00:00" or, with
// microseconds, "2026-01-08 10:05:00.123456+00:00" — the exact strings the
// existing result.json consumers already parse.
func pyDatetimeStr(t time.Time, withMicros bool) string {
	layout := "2006-01-02 15:04:05-07:00"
	if withMicros {
		layout = "2006-01-02 15:04:05.000000-07:00"
	}
	return t.Format(layout)
}
