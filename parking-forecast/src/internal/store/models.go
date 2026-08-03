// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package store

import (
	"database/sql"
	"time"
)

// SaveModel persists a station's serialized forest, replacing whatever was
// trained before it (there's exactly one current model per station, unlike
// the old 5x dnn_model* ensemble — see internal/forest for why a single
// forest already gives an ensemble-like spread).
func (db *DB) SaveModel(scode string, blob []byte, trainedAt time.Time, trainRows int) error {
	_, err := db.sql.Exec(`
		INSERT INTO models (scode, trained_at, train_rows, forest_blob) VALUES (?, ?, ?, ?)
		ON CONFLICT(scode) DO UPDATE SET trained_at = excluded.trained_at, train_rows = excluded.train_rows, forest_blob = excluded.forest_blob
	`, scode, trainedAt.Unix(), trainRows, blob)
	return err
}

func (db *DB) LoadModel(scode string) ([]byte, time.Time, bool, error) {
	var blob []byte
	var trainedAt int64
	err := db.sql.QueryRow(`SELECT forest_blob, trained_at FROM models WHERE scode = ?`, scode).Scan(&blob, &trainedAt)
	if err == sql.ErrNoRows {
		return nil, time.Time{}, false, nil
	}
	if err != nil {
		return nil, time.Time{}, false, err
	}
	return blob, time.Unix(trainedAt, 0).UTC(), true, nil
}

// StationsWithModels returns the station codes that currently have a trained
// model available.
func (db *DB) StationsWithModels() (map[string]bool, error) {
	rows, err := db.sql.Query(`SELECT scode FROM models`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	out := map[string]bool{}
	for rows.Next() {
		var scode string
		if err := rows.Scan(&scode); err != nil {
			return nil, err
		}
		out[scode] = true
	}
	return out, rows.Err()
}
