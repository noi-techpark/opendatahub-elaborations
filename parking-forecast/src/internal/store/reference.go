// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package store

// DayInfo mirrors the fields of the old data-holidays/holidays.csv (one row
// per calendar date).
type DayInfo struct {
	IsSchool  bool
	IsHoliday bool
}

func (db *DB) UpsertHolidays(byDate map[string]DayInfo) error {
	tx, err := db.sql.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	stmt, err := tx.Prepare(`
		INSERT INTO holidays (date, is_school, is_holiday) VALUES (?, ?, ?)
		ON CONFLICT(date) DO UPDATE SET is_school = excluded.is_school, is_holiday = excluded.is_holiday
	`)
	if err != nil {
		return err
	}
	defer stmt.Close()

	for date, info := range byDate {
		if _, err := stmt.Exec(date, boolToInt(info.IsSchool), boolToInt(info.IsHoliday)); err != nil {
			return err
		}
	}

	return tx.Commit()
}

func (db *DB) AllHolidays() (map[string]DayInfo, error) {
	rows, err := db.sql.Query(`SELECT date, is_school, is_holiday FROM holidays`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	out := map[string]DayInfo{}
	for rows.Next() {
		var date string
		var isSchool, isHoliday int
		if err := rows.Scan(&date, &isSchool, &isHoliday); err != nil {
			return nil, err
		}
		out[date] = DayInfo{IsSchool: isSchool != 0, IsHoliday: isHoliday != 0}
	}
	return out, rows.Err()
}

func (db *DB) UpsertWeather(byDate map[string]int) error {
	tx, err := db.sql.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	stmt, err := tx.Prepare(`
		INSERT INTO weather (date, symbol_value) VALUES (?, ?)
		ON CONFLICT(date) DO UPDATE SET symbol_value = excluded.symbol_value
	`)
	if err != nil {
		return err
	}
	defer stmt.Close()

	for date, symbol := range byDate {
		if _, err := stmt.Exec(date, symbol); err != nil {
			return err
		}
	}

	return tx.Commit()
}

func (db *DB) AllWeather() (map[string]int, error) {
	rows, err := db.sql.Query(`SELECT date, symbol_value FROM weather`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	out := map[string]int{}
	for rows.Next() {
		var date string
		var symbol int
		if err := rows.Scan(&date, &symbol); err != nil {
			return nil, err
		}
		out[date] = symbol
	}
	return out, rows.Err()
}

// LatestWeatherDate returns the most recent date cached, or "" if empty —
// used to compute the incremental fetch window (replaces data-meteo-get.sh's
// tail -n 1 trick).
func (db *DB) LatestWeatherDate() (string, error) {
	var date string
	err := db.sql.QueryRow(`SELECT COALESCE(MAX(date), '') FROM weather`).Scan(&date)
	return date, err
}

func boolToInt(b bool) int {
	if b {
		return 1
	}
	return 0
}
