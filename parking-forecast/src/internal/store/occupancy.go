// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package store

import (
	"database/sql"
	"time"
)

type OccPoint struct {
	TS    time.Time
	Value float64
}

// LastOccupancyTS returns the most recent cached timestamp for a station, used
// by ingest to compute the incremental catch-up window (replaces
// data-raw-get-diff.js's "last line of the CSV" approach).
func (db *DB) LastOccupancyTS(scode string) (time.Time, bool, error) {
	var unix int64
	err := db.sql.QueryRow(`SELECT last_ts FROM ingest_cursor WHERE scode = ?`, scode).Scan(&unix)
	if err == sql.ErrNoRows {
		return time.Time{}, false, nil
	}
	if err != nil {
		return time.Time{}, false, err
	}
	return time.Unix(unix, 0).UTC(), true, nil
}

// InsertOccupancy appends points for a station and advances its ingest cursor
// to the latest of them, in one transaction.
func (db *DB) InsertOccupancy(scode string, points []OccPoint) error {
	if len(points) == 0 {
		return nil
	}

	tx, err := db.sql.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	stmt, err := tx.Prepare(`INSERT OR REPLACE INTO occupancy (scode, ts, value) VALUES (?, ?, ?)`)
	if err != nil {
		return err
	}
	defer stmt.Close()

	last := points[0].TS
	for _, p := range points {
		if _, err := stmt.Exec(scode, p.TS.Unix(), p.Value); err != nil {
			return err
		}
		if p.TS.After(last) {
			last = p.TS
		}
	}

	if _, err := tx.Exec(`
		INSERT INTO ingest_cursor (scode, last_ts) VALUES (?, ?)
		ON CONFLICT(scode) DO UPDATE SET last_ts = excluded.last_ts
	`, scode, last.Unix()); err != nil {
		return err
	}

	return tx.Commit()
}

// OccupancyMap loads a station's cached occupancy between [from, to] (inclusive)
// into memory keyed by unix timestamp, for O(1) lag lookups while building
// feature rows. Ranges used by train/predict are bounded (a few weeks to
// months per station), so this comfortably fits in memory.
func (db *DB) OccupancyMap(scode string, from, to time.Time) (map[int64]float64, error) {
	rows, err := db.sql.Query(`
		SELECT ts, value FROM occupancy WHERE scode = ? AND ts BETWEEN ? AND ?
	`, scode, from.Unix(), to.Unix())
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	out := map[int64]float64{}
	for rows.Next() {
		var ts int64
		var v float64
		if err := rows.Scan(&ts, &v); err != nil {
			return nil, err
		}
		out[ts] = v
	}
	return out, rows.Err()
}

// PurgeOccupancyBefore deletes cached occupancy samples older than cutoff,
// across every station, so the occupancy table stays bounded regardless of
// how long ingest keeps running or how many stations it covers — see
// cmd/ingest and the OCCUPANCY_RETENTION_DAYS config. Returns the number of
// rows removed.
func (db *DB) PurgeOccupancyBefore(cutoff time.Time) (int64, error) {
	res, err := db.sql.Exec(`DELETE FROM occupancy WHERE ts < ?`, cutoff.Unix())
	if err != nil {
		return 0, err
	}
	return res.RowsAffected()
}

// EarliestOccupancyTS returns the oldest cached sample for a station, or ok=false
// if none is cached yet.
func (db *DB) EarliestOccupancyTS(scode string) (time.Time, bool, error) {
	var unix sql.NullInt64
	err := db.sql.QueryRow(`SELECT MIN(ts) FROM occupancy WHERE scode = ?`, scode).Scan(&unix)
	if err != nil {
		return time.Time{}, false, err
	}
	if !unix.Valid {
		return time.Time{}, false, nil
	}
	return time.Unix(unix.Int64, 0).UTC(), true, nil
}
