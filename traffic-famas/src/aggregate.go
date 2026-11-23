// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"fmt"
	"sort"
	"time"

	"github.com/noi-techpark/opendatahub-go-sdk/elab"
)

// Aggregation reduces all base values of one hourly window to a single value.
// To support another way of aggregating (min, max, median, ...), add it to aggregations.
type Aggregation func(values []float64) float64

var aggregations = map[string]Aggregation{
	"avg": func(v []float64) float64 { return sum(v) / float64(len(v)) },
	"sum": sum,
}

func sum(v []float64) float64 {
	var s float64
	for _, x := range v {
		s += x
	}
	return s
}

func lookupAggregation(name string) (Aggregation, error) {
	a, ok := aggregations[name]
	if !ok {
		return nil, fmt.Errorf("unknown aggregation %q, expected one of avg, sum", name)
	}
	return a, nil
}

type windowKey struct {
	dataType string
	end      time.Time
}

// aggregateStation groups the base measurements of a single station into windows of
// targetPeriod seconds and reduces each window with the aggregation configured for its data type.
//
// Windows are half-open [start, end), aligned to UTC, and the result is stamped with the window end.
// A window is only emitted once it is complete, meaning the last base bucket of the window has arrived,
// and when it contains at least minSamples records. Incomplete windows are skipped,
// they get picked up in a later run since the follower restarts at the last emitted timestamp.
func aggregateStation(s elab.Station, ms []elab.Measurement, aggs map[string]Aggregation, minSamples int) []elab.ElabResult {
	window := time.Duration(targetPeriod) * time.Second
	base := time.Duration(basePeriod) * time.Second

	groups := map[windowKey][]float64{}
	var newest time.Time
	for _, m := range ms {
		if m.Value.Num == nil {
			continue
		}
		ts := m.Timestamp.Time
		if ts.After(newest) {
			newest = ts
		}
		k := windowKey{m.TypeName, ts.UTC().Truncate(window).Add(window)}
		groups[k] = append(groups[k], *m.Value.Num)
	}

	results := []elab.ElabResult{}
	for k, values := range groups {
		agg, ok := aggs[k.dataType]
		if !ok {
			continue
		}
		// last base bucket of the window starts at end - base
		if newest.Before(k.end.Add(-base)) {
			continue
		}
		if len(values) < minSamples {
			continue
		}
		results = append(results, elab.ElabResult{
			Timestamp:   k.end,
			Period:      targetPeriod,
			StationType: s.Stationtype,
			StationCode: s.Stationcode,
			DataType:    k.dataType,
			Value:       agg(values),
		})
	}
	sort.Slice(results, func(i, j int) bool {
		if results[i].Timestamp.Equal(results[j].Timestamp) {
			return results[i].DataType < results[j].DataType
		}
		return results[i].Timestamp.Before(results[j].Timestamp)
	})
	return results
}
