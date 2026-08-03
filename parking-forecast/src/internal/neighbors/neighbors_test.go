// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package neighbors

import (
	"testing"

	"parking-forecast/internal/store"
)

func TestComputeNearestFirst(t *testing.T) {
	// Four stations roughly in a line, ~1km apart, all at the same latitude.
	stations := []store.Station{
		{Scode: "A", Lat: 46.5, Lon: 11.30},
		{Scode: "B", Lat: 46.5, Lon: 11.31},
		{Scode: "C", Lat: 46.5, Lon: 11.32},
		{Scode: "D", Lat: 46.5, Lon: 11.50}, // far away
	}

	got := Compute(stations, 2)

	byStation := map[string][]store.Neighbor{}
	for _, n := range got {
		byStation[n.Scode] = append(byStation[n.Scode], n)
	}

	aNeighbors := byStation["A"]
	if len(aNeighbors) != 2 {
		t.Fatalf("expected 2 neighbors for A, got %d", len(aNeighbors))
	}
	if aNeighbors[0].NeighborScode != "B" || aNeighbors[1].NeighborScode != "C" {
		t.Fatalf("expected A's neighbors ordered [B C], got %+v", aNeighbors)
	}
	if aNeighbors[0].DistanceM >= aNeighbors[1].DistanceM {
		t.Fatalf("expected increasing distance, got %+v", aNeighbors)
	}
	for _, n := range aNeighbors {
		if n.NeighborScode == "D" {
			t.Fatalf("D should never be closer than B/C for A")
		}
	}
}

func TestComputeCapsAtAvailableStations(t *testing.T) {
	stations := []store.Station{
		{Scode: "A", Lat: 46.5, Lon: 11.30},
		{Scode: "B", Lat: 46.5, Lon: 11.31},
	}
	got := Compute(stations, 5)
	count := 0
	for _, n := range got {
		if n.Scode == "A" {
			count++
		}
	}
	if count != 1 {
		t.Fatalf("expected 1 neighbor for A (only B available), got %d", count)
	}
}
