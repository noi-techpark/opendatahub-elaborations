// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

// Package holidays ports data-holidays-get.py: it derives per-day
// is_school/is_holiday flags from the Tourism Open Data Hub's school- and
// public-holiday Events, and caches them via internal/store instead of
// data-holidays/holidays.csv.
package holidays

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"time"

	"parking-forecast/internal/store"
)

const pageSize = 500

type eventsResponse struct {
	Items []struct {
		DateBegin string `json:"DateBegin"`
		DateEnd   string `json:"DateEnd"`
	} `json:"Items"`
}

func fetchEventDates(baseURL, tag string) (map[string]struct{}, error) {
	u, err := url.Parse(baseURL + "/Event")
	if err != nil {
		return nil, err
	}
	q := u.Query()
	q.Set("rawfilter", fmt.Sprintf("and(like(Tags,'%s'))", tag))
	q.Set("pagesize", fmt.Sprint(pageSize))
	u.RawQuery = q.Encode()

	resp, err := http.Get(u.String())
	if err != nil {
		return nil, fmt.Errorf("fetching %q events: %w", tag, err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("fetching %q events: status %d", tag, resp.StatusCode)
	}

	var parsed eventsResponse
	if err := json.NewDecoder(resp.Body).Decode(&parsed); err != nil {
		return nil, fmt.Errorf("decoding %q events: %w", tag, err)
	}

	dates := map[string]struct{}{}
	for _, item := range parsed.Items {
		begin, err := parseEventDate(item.DateBegin)
		if err != nil {
			continue
		}
		end, err := parseEventDate(item.DateEnd)
		if err != nil {
			continue
		}
		for d := begin; !d.After(end); d = d.AddDate(0, 0, 1) {
			dates[d.Format("2006-01-02")] = struct{}{}
		}
	}
	return dates, nil
}

func parseEventDate(s string) (time.Time, error) {
	if len(s) < 10 {
		return time.Time{}, fmt.Errorf("invalid date %q", s)
	}
	return time.Parse("2006-01-02", s[:10])
}

// FetchAndCache refreshes the holidays cache from the Tourism Open Data Hub
// and upserts it into db. It always refetches the full event set (school and
// public holiday calendars are small and published years ahead, so there's
// no meaningful "incremental" fetch here, unlike occupancy or weather).
func FetchAndCache(baseURL string, db *store.DB) error {
	schoolDates, err := fetchEventDates(baseURL, "school holiday")
	if err != nil {
		return err
	}
	publicDates, err := fetchEventDates(baseURL, "public holiday")
	if err != nil {
		return err
	}

	if len(schoolDates) == 0 && len(publicDates) == 0 {
		return nil
	}

	var minDate, maxDate time.Time
	for dateStr := range union(schoolDates, publicDates) {
		d, _ := time.Parse("2006-01-02", dateStr)
		if minDate.IsZero() || d.Before(minDate) {
			minDate = d
		}
		if maxDate.IsZero() || d.After(maxDate) {
			maxDate = d
		}
	}

	byDate := map[string]store.DayInfo{}
	for d := minDate; !d.After(maxDate); d = d.AddDate(0, 0, 1) {
		key := d.Format("2006-01-02")
		_, isSchoolHoliday := schoolDates[key]
		_, isPublicHoliday := publicDates[key]
		isWeekend := d.Weekday() == time.Saturday || d.Weekday() == time.Sunday

		byDate[key] = store.DayInfo{
			IsSchool:  !(isWeekend || isSchoolHoliday || isPublicHoliday),
			IsHoliday: isPublicHoliday || isWeekend,
		}
	}

	return db.UpsertHolidays(byDate)
}

func union(a, b map[string]struct{}) map[string]struct{} {
	out := make(map[string]struct{}, len(a)+len(b))
	for k := range a {
		out[k] = struct{}{}
	}
	for k := range b {
		out[k] = struct{}{}
	}
	return out
}
