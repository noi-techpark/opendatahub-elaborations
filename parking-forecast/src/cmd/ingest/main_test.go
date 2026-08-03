// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"fmt"
	"testing"

	"parking-forecast/internal/odh"
)

func TestChunkByURLLengthRespectsBothBounds(t *testing.T) {
	// short codes: only maxBatchStations should kick in
	pending := make([]pendingStation, maxBatchStations*2+7)
	for i := range pending {
		pending[i] = pendingStation{station: odh.StationInfo{Scode: fmt.Sprintf("%d", i)}}
	}
	chunks := chunkByURLLength(pending)

	total := 0
	for _, c := range chunks {
		if len(c) > maxBatchStations {
			t.Fatalf("chunk exceeds maxBatchStations: %d", len(c))
		}
		total += len(c)
	}
	if total != len(pending) {
		t.Fatalf("chunking dropped stations: got %d, want %d", total, len(pending))
	}
	if len(chunks) != 3 {
		t.Fatalf("expected 3 chunks (2 full + remainder), got %d", len(chunks))
	}
}

func TestChunkByURLLengthRespectsCharBudget(t *testing.T) {
	// long codes: URL length should kick in well before maxBatchStations
	longCode := "TRENTO:some-quite-long-station-code-here"
	pending := make([]pendingStation, 100)
	for i := range pending {
		pending[i] = pendingStation{station: odh.StationInfo{Scode: longCode}}
	}
	chunks := chunkByURLLength(pending)

	for _, c := range chunks {
		urlChars := 0
		for _, p := range c {
			urlChars += len(p.station.Scode) + 3
		}
		if urlChars > maxBatchURLChars {
			t.Fatalf("chunk exceeds maxBatchURLChars: %d", urlChars)
		}
	}
	if len(chunks) < 2 {
		t.Fatalf("expected multiple chunks given long codes, got %d", len(chunks))
	}
}

func TestChunkByURLLengthEmpty(t *testing.T) {
	if chunks := chunkByURLLength(nil); chunks != nil {
		t.Fatalf("expected nil for empty input, got %v", chunks)
	}
}
