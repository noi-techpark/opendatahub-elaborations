// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

// Package publish renders a batch of per-station forecasts as the legacy
// result.json file documented in readme-for-data-consumers.md.
//
// Publishing forecasts as native ODH/BDP time series is planned but not
// implemented yet.
package publish

import "time"

// Point is one forecast timestep for a station, already converted to
// occupancy-count units (ratio * capacity, clipped to [0, capacity]). A nil
// pointer means "unknown" (station couldn't be forecast, e.g. not enough
// history yet) and is rendered as JSON null, exactly as documented for
// consumers today.
type Point struct {
	TS           time.Time
	Lo, Mean, Hi *float64
}

type StationForecast struct {
	Scode  string
	Points []Point
}
