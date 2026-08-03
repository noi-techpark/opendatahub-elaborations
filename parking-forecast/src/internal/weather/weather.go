// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

// Package weather ports data-meteo-get.sh: it pulls the daily weather symbol
// forecast (station id 3 of the Tourism Open Data Hub's WeatherHistory feed)
// and caches it via internal/store instead of data-meteo/meteo.csv.
package weather

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"

	"parking-forecast/internal/store"
)

// stationID 3 is the "province-wide" forecast used by the old pipeline
// (data-meteo-get.sh: `select(.Id == 3)`).
const stationID = 3

// defaultFrom mirrors data-meteo-get.sh's hardcoded starting point for a cold cache.
const defaultFrom = "2021-12-31"

type weatherHistoryResponse struct {
	Items []struct {
		Stationdata []struct {
			ID          int    `json:"Id"`
			Date        string `json:"date"`
			WeatherCode string `json:"WeatherCode"`
		} `json:"Weather.en.Stationdata"`
	} `json:"Items"`
}

// FetchAndCache fetches weather symbols from the given date onward (or the
// latest cached date, whichever is more recent) and upserts them into db.
func FetchAndCache(baseURL string, db *store.DB) error {
	from, err := db.LatestWeatherDate()
	if err != nil {
		return fmt.Errorf("reading latest cached weather date: %w", err)
	}
	if from == "" {
		from = defaultFrom
	}

	u, err := url.Parse(baseURL + "/WeatherHistory")
	if err != nil {
		return err
	}
	q := u.Query()
	q.Set("rawsort", "_Meta.LastUpdate")
	q.Set("fields", "Weather.en.Stationdata")
	q.Set("pagesize", "0")
	q.Set("datefrom", from)
	u.RawQuery = q.Encode()

	resp, err := http.Get(u.String())
	if err != nil {
		return fmt.Errorf("fetching weather history: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("fetching weather history: status %d", resp.StatusCode)
	}

	var parsed weatherHistoryResponse
	if err := json.NewDecoder(resp.Body).Decode(&parsed); err != nil {
		return fmt.Errorf("decoding weather history: %w", err)
	}

	byDate := map[string]int{}
	for _, item := range parsed.Items {
		for _, sd := range item.Stationdata {
			if sd.ID != stationID {
				continue
			}
			date := sd.Date
			if len(date) >= 10 {
				date = date[:10]
			}
			symbol, ok := weatherCodeToSymbol(sd.WeatherCode)
			if !ok {
				continue
			}
			// Duplicate dates (a "today" and a "tomorrow" prediction can
			// both cover the same day) resolve to whichever comes last in
			// the response, same as the old pipeline's awk dedup.
			byDate[date] = symbol
		}
	}

	if len(byDate) == 0 {
		return nil
	}
	return db.UpsertWeather(byDate)
}

// weatherCodeToSymbol maps a single a-z letter code to the 0-25 ordinal the
// model expects (same mapping as data-meteo-get.sh's `ord(letter) - 97`).
func weatherCodeToSymbol(code string) (int, bool) {
	if len(code) == 0 {
		return 0, false
	}
	c := code[0]
	if c < 'a' || c > 'z' {
		return 0, false
	}
	return int(c - 'a'), true
}
