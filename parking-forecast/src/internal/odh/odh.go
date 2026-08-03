// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

// Package odh wraps this org's standard go-timeseries-client/elab SDKs for
// what the parking forecast jobs need to read from Open Data Hub: station
// metadata and occupancy history. It deliberately reuses
// elab.Elaboration's RequestState/RequestHistory instead of
// re-implementing pagination and auth.
//
// Publishing forecasts back to Open Data Hub isn't wired up yet — that
// migration is planned for later — so this package has no write path for
// now.
package odh

import (
	"time"

	"github.com/noi-techpark/go-bdp-client/bdplib"
	"github.com/noi-techpark/go-timeseries-client/odhts"
	"github.com/noi-techpark/opendatahub-go-sdk/elab"

	"parking-forecast/internal/config"
)

type Client struct {
	elab            elab.Elaboration
	occupancyType   string
	occupancyPeriod elab.Period
}

func New(cfg config.Env) *Client {
	ts := odhts.NewCustomClient(cfg.TsApiBaseUrl, cfg.OdhTokenUrl, cfg.TsApiReferer)
	ts.UseAuth(cfg.OdhClientId, cfg.OdhClientSecret)

	// elab.NewElaboration requires a bdplib.Bdp, but we only ever call its
	// read-side methods (RequestState/RequestHistory), so an unconfigured
	// one is fine — there's nothing to publish to yet.
	bdp := bdplib.FromEnv(bdplib.BdpEnv{})

	e := elab.NewElaboration(&ts, &bdp)
	e.StationTypes = cfg.StationTypes
	e.BaseTypes = []elab.BaseDataType{{Name: cfg.OccupancyType, Period: cfg.OccupancyPeriod}}

	return &Client{
		elab:            e,
		occupancyType:   cfg.OccupancyType,
		occupancyPeriod: cfg.OccupancyPeriod,
	}
}

// StationInfo is the subset of ODH station metadata the forecast needs.
type StationInfo struct {
	Scode           string
	Name            string
	StationType     string
	Lat, Lon        float64
	Capacity        float64 // parking spaces; a ParkingSensor covers exactly one, so its capacity is always 1
	LastOccupancyTS time.Time
	HasOccupancyTS  bool
}

// FetchStations returns every active station of the configured station types,
// along with the latest occupancy timestamp ODH has for each — the "to" bound
// ingest needs to compute its catch-up window, obtained for free from the
// same tree-node request that gives us station metadata.
func (c *Client) FetchStations() ([]StationInfo, error) {
	state, err := c.elab.RequestState()
	if err != nil {
		return nil, err
	}

	var out []StationInfo
	for _, stp := range state {
		for scode, st := range stp.Stations {
			// ParkingSensor stations are single-space sensors (occupied =
			// 0 or 1) and don't carry a "capacity" metadata field; only
			// ParkingStation aggregates do. Same convention as
			// parking-free-slot-calculation.
			capacity := 1.0
			if st.Station.Stationtype == "ParkingStation" {
				capacity = 0
				if v, ok := st.Station.Metadata["capacity"]; ok {
					if f, ok := v.(float64); ok {
						capacity = f
					}
				}
			}

			info := StationInfo{
				Scode:       scode,
				Name:        st.Station.Name,
				StationType: st.Station.Stationtype,
				Lat:         float64(st.Station.Coord.Y),
				Lon:         float64(st.Station.Coord.X),
				Capacity:    capacity,
			}
			if dt, ok := st.Datatypes[c.occupancyType]; ok {
				if ts, ok := dt.Periods[c.occupancyPeriod]; ok && !ts.IsZero() {
					info.LastOccupancyTS = ts
					info.HasOccupancyTS = true
				}
			}
			out = append(out, info)
		}
	}
	return out, nil
}

// FetchOccupancyHistory pulls raw occupancy measurements for one station type
// and a set of station codes in the half-open interval [from, to).
func (c *Client) FetchOccupancyHistory(stationType string, scodes []string, from, to time.Time) ([]elab.Measurement, error) {
	if len(scodes) == 0 || !to.After(from) {
		return nil, nil
	}
	return c.elab.RequestHistory([]string{stationType}, scodes, []string{c.occupancyType}, []elab.Period{c.occupancyPeriod}, from, to)
}
