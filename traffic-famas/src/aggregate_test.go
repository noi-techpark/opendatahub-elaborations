// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"testing"
	"time"

	"github.com/noi-techpark/go-timeseries-client/odhts"
	"github.com/noi-techpark/opendatahub-go-sdk/elab"
)

func meas(typ string, ts time.Time, v float64) elab.Measurement {
	return elab.Measurement{
		TypeName:  typ,
		Timestamp: odhts.TsTime{Time: ts},
		Value:     elab.MeasurementValue{Type: elab.MTypeFloat, Num: &v},
	}
}

// 12 buckets of 5 minutes starting at start, with value v+i
func hour(typ string, start time.Time, v float64, n int) []elab.Measurement {
	var ms []elab.Measurement
	for i := 0; i < n; i++ {
		ms = append(ms, meas(typ, start.Add(time.Duration(i)*5*time.Minute), v+float64(i)))
	}
	return ms
}

func aggs(name string, types ...string) map[string]Aggregation {
	a, _ := lookupAggregation(name)
	m := map[string]Aggregation{}
	for _, t := range types {
		m[t] = a
	}
	return m
}

var t0 = time.Date(2026, 1, 1, 10, 0, 0, 0, time.UTC)
var st = elab.Station{Stationcode: "3:lane", Stationtype: TRAFFIC_SENSOR}

func TestAvgAndSum(t *testing.T) {
	ms := hour("total-transits", t0, 10, 12) // 10..21 -> sum 186
	for name, want := range map[string]float64{"avg": 15.5, "sum": 186} {
		agg := aggs(name, "total-transits")
		// a 13th record in the next hour proves nothing more, window of 10:00 is complete anyway
		res := aggregateStation(st, ms, agg, 1)
		if len(res) != 1 {
			t.Fatalf("%s: expected 1 result, got %d", name, len(res))
		}
		r := res[0]
		if r.Value.(float64) != want || !r.Timestamp.Equal(t0.Add(time.Hour)) || r.Period != 3600 || r.DataType != "total-transits" {
			t.Errorf("%s: unexpected result %+v", name, r)
		}
	}
}

func TestIncompleteWindowSkipped(t *testing.T) {
	agg := aggs("avg", "total-transits")
	ms := hour("total-transits", t0, 1, 12)
	ms = append(ms, hour("total-transits", t0.Add(time.Hour), 1, 5)...) // 11:00 window not finished
	res := aggregateStation(st, ms, agg, 1)
	if len(res) != 1 || !res[0].Timestamp.Equal(t0.Add(time.Hour)) {
		t.Fatalf("expected only the 10:00 window, got %+v", res)
	}
}

func TestMinSamples(t *testing.T) {
	agg := aggs("avg", "headway")
	ms := hour("headway", t0, 1, 4)
	ms = append(ms, meas("total-transits", t0.Add(55*time.Minute), 1)) // completes the window
	res := aggregateStation(st, ms, agg, 5)
	if len(res) != 0 {
		t.Fatalf("expected nothing below MIN_SAMPLES, got %+v", res)
	}
	if res := aggregateStation(st, ms, agg, 4); len(res) != 1 || res[0].DataType != "headway" {
		t.Fatalf("expected headway result, got %+v", res)
	}
}

func TestMultipleTypesAndHours(t *testing.T) {
	agg := aggs("sum", "gap", "headway")
	var ms []elab.Measurement
	for _, typ := range []string{"gap", "headway"} {
		ms = append(ms, hour(typ, t0, 0, 24)...)
	}
	res := aggregateStation(st, ms, agg, 1)
	if len(res) != 4 {
		t.Fatalf("expected 4 results, got %d", len(res))
	}
}

func TestUnknownAggregation(t *testing.T) {
	if _, err := lookupAggregation("median"); err == nil {
		t.Fatal("expected error")
	}
}

func TestPerTypeAggregation(t *testing.T) {
	sumA, _ := lookupAggregation("sum")
	avgA, _ := lookupAggregation("avg")
	a := map[string]Aggregation{"total-transits": sumA, "headway": avgA}
	ms := append(hour("total-transits", t0, 10, 12), hour("headway", t0, 10, 12)...)
	ms = append(ms, hour("unconfigured", t0, 10, 12)...)
	got := map[string]float64{}
	for _, r := range aggregateStation(st, ms, a, 1) {
		got[r.DataType] = r.Value.(float64)
	}
	if len(got) != 2 || got["total-transits"] != 186 || got["headway"] != 15.5 {
		t.Fatalf("unexpected %+v", got)
	}
}
