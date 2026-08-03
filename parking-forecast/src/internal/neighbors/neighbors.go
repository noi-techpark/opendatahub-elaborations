// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

// Package neighbors computes, for every station, its k geographically
// nearest other stations. The forecast model uses this as a proxy for
// spatial/area-wide effects (an event or a storm makes a whole
// neighbourhood busier or emptier together), without needing per-neighbor
// features that would grow with the size of the network.
package neighbors

import (
	"math"
	"sort"

	"parking-forecast/internal/store"
)

const earthRadiusM = 6371000.0

// Compute returns, for every station, its k nearest neighbors by great-circle
// distance (station coordinates from ODH are WGS84 lon/lat degrees).
// O(n^2); fine for the station counts this runs over (recomputed only when
// the station list changes, not per prediction step).
func Compute(stations []store.Station, k int) []store.Neighbor {
	var out []store.Neighbor

	for _, s := range stations {
		type candidate struct {
			scode string
			dist  float64
		}
		candidates := make([]candidate, 0, len(stations)-1)
		for _, other := range stations {
			if other.Scode == s.Scode {
				continue
			}
			d := haversineMeters(s.Lat, s.Lon, other.Lat, other.Lon)
			candidates = append(candidates, candidate{other.Scode, d})
		}
		sort.Slice(candidates, func(i, j int) bool { return candidates[i].dist < candidates[j].dist })

		n := k
		if n > len(candidates) {
			n = len(candidates)
		}
		for i := 0; i < n; i++ {
			out = append(out, store.Neighbor{
				Scode:         s.Scode,
				Rank:          i,
				NeighborScode: candidates[i].scode,
				DistanceM:     candidates[i].dist,
			})
		}
	}

	return out
}

func haversineMeters(lat1, lon1, lat2, lon2 float64) float64 {
	toRad := func(deg float64) float64 { return deg * math.Pi / 180 }

	phi1, phi2 := toRad(lat1), toRad(lat2)
	dPhi := toRad(lat2 - lat1)
	dLambda := toRad(lon2 - lon1)

	a := math.Sin(dPhi/2)*math.Sin(dPhi/2) +
		math.Cos(phi1)*math.Cos(phi2)*math.Sin(dLambda/2)*math.Sin(dLambda/2)
	c := 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))

	return earthRadiusM * c
}
