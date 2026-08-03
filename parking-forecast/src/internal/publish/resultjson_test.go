// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package publish

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestWriteResultJSONMatchesDocumentedSchema(t *testing.T) {
	start := time.Date(2026, 1, 8, 10, 5, 0, 0, time.UTC)
	lo, mean, hi := 10.4, 12.0, 13.6

	path := filepath.Join(t.TempDir(), "result.json")
	err := WriteResultJSON(path, start, 48, "2.0", []StationForecast{
		{
			Scode: "STATION1",
			Points: []Point{
				{TS: start, Lo: &lo, Mean: &mean, Hi: &hi},
				{TS: start.Add(5 * time.Minute)}, // all-null point
			},
		},
	})
	if err != nil {
		t.Fatalf("WriteResultJSON: %v", err)
	}

	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("reading result.json: %v", err)
	}

	var doc map[string]any
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatalf("result.json is not valid JSON: %v", err)
	}

	for _, key := range []string{"publish_timestamp", "forecast_start_timestamp", "forecast_period_seconds",
		"forecast_duration_hours", "model_version", "schema_version", "timeseries"} {
		if _, ok := doc[key]; !ok {
			t.Fatalf("missing documented top-level key %q", key)
		}
	}

	if doc["forecast_start_timestamp"] != "2026-01-08 10:05:00+00:00" {
		t.Fatalf("forecast_start_timestamp = %v, want python-style datetime string", doc["forecast_start_timestamp"])
	}
	if doc["forecast_period_seconds"].(float64) != 300 {
		t.Fatalf("forecast_period_seconds = %v, want 300", doc["forecast_period_seconds"])
	}

	timeseries := doc["timeseries"].(map[string]any)
	points := timeseries["STATION1"].([]any)
	if len(points) != 2 {
		t.Fatalf("expected 2 points, got %d", len(points))
	}

	first := points[0].(map[string]any)
	for _, key := range []string{"ts", "lo", "mean", "hi", "rmse"} {
		if _, ok := first[key]; !ok {
			t.Fatalf("point missing documented key %q", key)
		}
	}
	if first["lo"].(float64) != 10.4 || first["mean"].(float64) != 12.0 || first["hi"].(float64) != 13.6 {
		t.Fatalf("unexpected point values: %+v", first)
	}
	if first["rmse"] != nil {
		t.Fatalf("rmse should always be null (disabled upstream), got %v", first["rmse"])
	}

	second := points[1].(map[string]any)
	if second["lo"] != nil || second["mean"] != nil || second["hi"] != nil {
		t.Fatalf("expected an all-null second point, got %+v", second)
	}
}
