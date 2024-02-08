// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package dc

import (
	"fmt"
	"log/slog"
	"strconv"
	"time"
	"traffic-a22-data-quality/bdplib"
	"traffic-a22-data-quality/ninja"
)

type NinjaMeasurement struct {
	Period uint64          `json:"mperiod"`
	Time   ninja.NinjaTime `json:"mvalidtime"`
	Since  ninja.NinjaTime `json:"mtransactiontime"`
}

type NinjaTreeData = map[string]struct { // key = stationtype
	Stations map[string]struct { // key = stationcode
		Datatypes map[string]struct { // key = datatype
			Measurements []NinjaMeasurement `json:"tmeasurements"`
		} `json:"sdatatypes"`
	} `json:"stations"`
}

type NinjaFlatData = struct {
	Timestamp ninja.NinjaTime `json:"_timestamp"`
	Value     uint64          `json:"mvalue"`
}

func sumSingleTypes() {
	// Get current elaboration state from ninja. Both where we are with base data and with the sums

	req := ninja.DefaultNinjaRequest()
	req.Repr = ninja.TreeNode
	req.StationTypes = append(req.StationTypes, stationType)
	req.DataTypes = dataTypes
	req.Limit = -1
	req.Select = "mperiod,mvalidtime"
	req.Where = fmt.Sprintf("mperiod.in.(%d,%d)", periodBase, periodAggregate)

	var res ninja.NinjaResponse[NinjaTreeData]
	err := ninja.Latest(req, &res)
	if err != nil {
		slog.Error("error", err)
		return
	}

	requestWindows := getRequestWindows(res)

	// 	get data history from starting point until last EOD
	for stationCode, typeMap := range requestWindows {
		recs := bdplib.DataMap{}
		totals := make(map[time.Time]uint64)
		for typeName, todo := range typeMap {
			// debugLogJson(res)
			history, err := getBaseHistory(todo, stationCode, typeName)
			if err != nil {
				slog.Error("Error requesting history data from Ninja", "err", err)
				return
			}

			slog.Info(strconv.Itoa(len(history)))

			if len(history) == 0 {
				continue
			}

			sums := make(map[time.Time]uint64)
			for _, m := range history {
				date := stripToDay(m.Timestamp.Time)
				sums[date] = sums[date] + m.Value
				totals[date] = totals[date] + m.Value
			}
			for date, sum := range sums {
				recs.AddRecord(stationCode, typeName, bdplib.CreateRecord(date.UnixMilli(), sum, periodAggregate))
			}
		}
		bdplib.PushData(stationType, recs)
	}
}

func getBaseHistory(todo todoStation, stationCode string, typeName string) ([]NinjaFlatData, error) {
	var ret []NinjaFlatData
	for page := 0; ; page += 1 {
		start, end := getRequestDates(todo)

		res, err := getNinjaData(stationCode, typeName, start, end, page)
		if err != nil {
			return nil, err
		}

		if len(ret) == 0 {
			ret = res.Data
		} else {
			ret = append(ret, res.Data...)
		}

		// only if limit = length, there might be more data
		if res.Limit != int64(len(res.Data)) {
			break
		} else {
			slog.Debug("Using pagination to request more data: ", "limit", res.Limit, "data.length", len(res.Data), "offset", page, "firstDate", res.Data[0].Timestamp.Time)
		}
	}
	return ret, nil
}

func getRequestWindows(res ninja.NinjaResponse[NinjaTreeData]) map[string]map[string]todoStation {
	todos := make(map[string]map[string]todoStation)
	for _, stations := range res.Data {
		for stationCode, station := range stations.Stations {
			for typeName, dataType := range station.Datatypes {
				for _, m := range dataType.Measurements {
					var firstBase time.Time
					var lastBase time.Time
					var lastAggregate time.Time
					if m.Period == uint64(periodBase) {
						lastBase = m.Time.Time
						firstBase = m.Since.Time
					}
					if m.Period == periodAggregate {
						lastAggregate = m.Time.Time
					}

					// only consider stations that don't have up to date aggregates
					if lastBase.Sub(lastAggregate).Seconds() > periodAggregate {
						if todos[stationCode] == nil {
							todos[stationCode] = make(map[string]todoStation)
						}
						todos[stationCode][typeName] = todoStation{
							firstBase:     firstBase,
							lastBase:      lastBase,
							lastAggregate: lastAggregate,
						}
					}
				}
			}
		}
	}
	return todos
}

func stripToDay(t time.Time) time.Time {
	return time.Date(t.Year(), t.Month(), t.Day(), 0, 0, 0, 0, t.Location())
}

type todoStation struct {
	firstBase     time.Time
	lastBase      time.Time
	lastAggregate time.Time
}

func getRequestDates(todo todoStation) (time.Time, time.Time) {
	start := todo.lastAggregate
	if start.Before(todo.firstBase) {
		start = todo.firstBase
	}

	start = stripToDay(start).AddDate(0, 0, 1)
	end := stripToDay(todo.lastBase)
	return start, end
}

func getNinjaData(stationCode string, typeName string, from time.Time, to time.Time, offset int) (*ninja.NinjaResponse[[]NinjaFlatData], error) {
	req := ninja.DefaultNinjaRequest()
	req.AddDataType(typeName)
	req.From = from
	req.To = to
	req.Select = "mvalue"
	req.Where = fmt.Sprintf("and(mperiod.eq.%d,scode.eq.\"%s\")", periodBase, stationCode)
	req.Limit = int64(ninjaLimit)
	req.Offset = uint64(offset * int(req.Limit))
	req.Shownull = false

	res := &ninja.NinjaResponse[[]NinjaFlatData]{}

	err := ninja.History(req, res)
	return res, err
}

func totalJob() {
	totalType := bdplib.CreateDataType("Nr. Vehicles", "", "Number of vehicles", "total")
	bdplib.SyncDataTypes(stationType, []bdplib.DataType{totalType})

	req := ninja.DefaultNinjaRequest()
	req.Repr = ninja.TreeNode
	req.StationTypes = append(req.StationTypes, stationType, parentStationType)
	req.DataTypes = append(dataTypes, totalType.Name)
	req.Limit = -1
	req.Select = "mperiod,mvalidtime"
	req.Where = fmt.Sprintf("mperiod.in.(%d,%d)", periodBase, periodAggregate)

	var res ninja.NinjaResponse[NinjaTreeData]
	err := ninja.Latest(req, &res)
	if err != nil {
		slog.Error("error", err)
		return
	}

	requestWindows := getRequestWindows(res)

	// 	get data history from starting point until last EOD
	for stationCode, typeMap := range requestWindows {
		recs := bdplib.DataMap{}
		totals := make(map[time.Time]uint64)
		for typeName, todo := range typeMap {
			// debugLogJson(res)
			history, err := getBaseHistory(todo, stationCode, typeName)
			if err != nil {
				slog.Error("Error requesting history data from Ninja", "err", err)
				return
			}

			slog.Info(strconv.Itoa(len(history)))

			if len(history) == 0 {
				continue
			}

			sums := make(map[time.Time]uint64)
			for _, m := range history {
				date := stripToDay(m.Timestamp.Time)
				sums[date] = sums[date] + m.Value
				totals[date] = totals[date] + m.Value
			}
			for date, sum := range sums {
				recs.AddRecord(stationCode, typeName, bdplib.CreateRecord(date.UnixMilli(), sum, periodAggregate))
			}
		}
		for date, total := range totals {
			recs.AddRecord(stationCode, totalType.Name, bdplib.CreateRecord(date.UnixMilli(), total, periodAggregate))
		}
		bdplib.PushData(stationType, recs)
	}

}
