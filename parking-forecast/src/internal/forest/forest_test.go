// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package forest

import (
	"math"
	"math/rand"
	"testing"
)

// TestFitRecoversSignal checks the forest learns a simple non-linear,
// interaction-bearing function (the kind of hour-x-weather interaction we
// rely on it to pick up automatically) substantially better than predicting
// the mean.
func TestFitRecoversSignal(t *testing.T) {
	rng := rand.New(rand.NewSource(42))

	n := 4000
	X := make([][]float64, n)
	y := make([]float64, n)
	for i := 0; i < n; i++ {
		hour := rng.Float64() * 24
		weather := math.Round(rng.Float64() * 3) // 0..3
		X[i] = []float64{hour, weather}
		// interaction: weather only matters during "peak" hours
		peak := 0.0
		if hour > 7 && hour < 10 {
			peak = 1.0
		}
		noise := rng.NormFloat64() * 0.05
		y[i] = 0.3 + 0.5*peak - 0.2*peak*weather + noise
	}

	cfg := DefaultConfig()
	cfg.NumTrees = 30
	f := Fit(X, y, cfg)

	// held-out test points
	sse, sseBaseline := 0.0, 0.0
	meanY := 0.0
	for _, v := range y {
		meanY += v
	}
	meanY /= float64(n)

	testN := 500
	for i := 0; i < testN; i++ {
		hour := rng.Float64() * 24
		weather := math.Round(rng.Float64() * 3)
		peak := 0.0
		if hour > 7 && hour < 10 {
			peak = 1.0
		}
		want := 0.3 + 0.5*peak - 0.2*peak*weather

		mean, lo, hi := f.PredictStats([]float64{hour, weather}, 0.1, 0.9)
		if lo > hi {
			t.Fatalf("lo (%v) > hi (%v)", lo, hi)
		}
		if lo > mean || hi < mean {
			t.Fatalf("mean %v not within [lo,hi] = [%v,%v]", mean, lo, hi)
		}

		sse += (mean - want) * (mean - want)
		sseBaseline += (meanY - want) * (meanY - want)
	}

	if sse >= sseBaseline*0.3 {
		t.Fatalf("forest barely beat the mean-only baseline: sse=%v baselineSse=%v", sse, sseBaseline)
	}
}

func TestMarshalRoundTrip(t *testing.T) {
	rng := rand.New(rand.NewSource(1))
	n := 200
	X := make([][]float64, n)
	y := make([]float64, n)
	for i := 0; i < n; i++ {
		X[i] = []float64{rng.Float64(), rng.Float64()}
		y[i] = X[i][0] + 2*X[i][1]
	}
	cfg := DefaultConfig()
	cfg.NumTrees = 5
	f := Fit(X, y, cfg)

	blob, err := Marshal(f)
	if err != nil {
		t.Fatal(err)
	}
	f2, err := Unmarshal(blob)
	if err != nil {
		t.Fatal(err)
	}

	x := []float64{0.4, 0.6}
	m1, _, _ := f.PredictStats(x, 0.1, 0.9)
	m2, _, _ := f2.PredictStats(x, 0.1, 0.9)
	if m1 != m2 {
		t.Fatalf("prediction mismatch after roundtrip: %v vs %v", m1, m2)
	}
}
