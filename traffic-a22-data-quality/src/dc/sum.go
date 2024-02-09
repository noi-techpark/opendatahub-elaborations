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

	"golang.org/x/exp/maps"
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

func sumJob() {
	// Get current elaboration state from ninja. Both where we are with base data and with the sums

	req := ninja.DefaultNinjaRequest()
	req.Repr = ninja.TreeNode
	req.AddStationType(baseStationType)
	req.DataTypes = baseDataTypes
	req.Limit = -1
	req.Select = "mperiod,mvalidtime,pcode"
	req.Where = fmt.Sprintf("and(sactive.eq.true,mperiod.in.(%d,%d))", basePeriod, periodAggregate)

	var res ninja.NinjaResponse[NinjaTreeData]
	err := ninja.Latest(req, &res)
	if err != nil {
		slog.Error("error", err)
		return
	}

	requestWindows := requestWindows(res)

	// 	get data history from starting point until last EOD
	for stationCode, typeMap := range requestWindows {
		recs := bdplib.DataMap{}
		totals := make(map[time.Time]uint64)
		for typeName, todo := range typeMap {
			history, err := getHistoryPaged(todo, stationCode, typeName)
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
			recs.AddRecord(stationCode, TotalType.Name, bdplib.CreateRecord(date.UnixMilli(), total, periodAggregate))
		}
		bdplib.PushData(baseStationType, recs)
	}
}

func getHistoryPaged(todo todoStation, stationCode string, typeName string) ([]NinjaFlatData, error) {
	var ret []NinjaFlatData
	for page := 0; ; page += 1 {
		start, end := getRequestDates(todo)

		res, err := getNinjaData(stationCode, typeName, start, end, page)
		if err != nil {
			return nil, err
		}

		ret = append(ret, res.Data...)

		// only if limit = length, there might be more data
		if res.Limit != int64(len(res.Data)) {
			break
		} else {
			slog.Debug("Using pagination to request more data: ", "limit", res.Limit, "data.length", len(res.Data), "offset", page, "firstDate", res.Data[0].Timestamp.Time)
		}
	}
	return ret, nil
}

func requestWindows(res ninja.NinjaResponse[NinjaTreeData]) map[string]map[string]todoStation {
	todos := make(map[string]map[string]todoStation)
	for _, stations := range res.Data {
		for stationCode, station := range stations.Stations {
			for typeName, dataType := range station.Datatypes {
				for _, m := range dataType.Measurements {
					var firstBase time.Time
					var lastBase time.Time
					var lastAggregate time.Time
					if m.Period == uint64(basePeriod) {
						lastBase = m.Time.Time
						firstBase = m.Since.Time
					}
					if m.Period == periodAggregate {
						lastAggregate = m.Time.Time
					}

					// only consider stations that don't have up to date aggregates
					if lastBase.Sub(lastAggregate).Seconds() > periodAggregate {
						if _, exists := todos[stationCode]; !exists {
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
	req.Where = fmt.Sprintf("and(mperiod.eq.%d,scode.eq.\"%s\")", basePeriod, stationCode)
	req.Limit = int64(sumRequestLimit)
	req.Offset = uint64(offset * int(req.Limit))

	res := &ninja.NinjaResponse[[]NinjaFlatData]{}

	err := ninja.History(req, res)
	return res, err
}

func sumParentJob() {
	req := ninja.DefaultNinjaRequest()
	req.DataTypes = append(baseDataTypes, TotalType.Name)
	req.Select = "tname,mvalue,pcode,stype"
	req.Where = fmt.Sprintf("sorigin.eq.%s,sactive.eq.true,mperiod.eq.%d", origin, periodAggregate)
	req.Limit = -1

	res := &ninja.NinjaResponse[[]struct {
		Tstamp ninja.NinjaTime `json:"_timestamp"`
		DType  string          `json:"tname"`
		Value  uint64          `json:"mvalue"`
		Parent string          `json:"pcode"`
		Stype  string          `json:"stype"`
	}]{}

	err := ninja.Latest(req, res)
	if err != nil {
		slog.Error("sumParent: Error in ninja call. aborting", "err", err)
		return
	}

	type window = struct {
		from time.Time
		to   time.Time
	}

	// parentId / datatype
	parents := make(map[string]map[string]window)

	// For each parent/type find out where the elaboration window starts/ends
	for _, m := range res.Data {
		if _, exists := parents[m.Parent]; !exists {
			parents[m.Parent] = make(map[string]window)
		}
		t := parents[m.Parent][m.DType]
		// There is only one parent record per data type
		if m.Stype == parentStationType {
			t.from = m.Tstamp.Time
		} else {
			if m.Tstamp.Time.After(t.to) {
				t.to = m.Tstamp.Time
			}
		}
		parents[m.Parent][m.DType] = t
	}

	for parId, types := range parents {
		// Do only a single request per parent. So we determine the max window.
		// Note that when a data type does not exist yet on parent station, but in a child station, the window defaults to from = 0000-00-00...
		var from time.Time
		var to time.Time
		for _, tp := range types {
			if tp.from.Before(from) {
				from = tp.from
			}
			if tp.to.After(to) {
				to = tp.to
			}
		}

		req := ninja.DefaultNinjaRequest()
		req.DataTypes = maps.Keys(types) // Any data type we found base data for
		req.AddStationType(baseStationType)
		req.Select = "tname,mvalue"
		req.From = from
		req.To = to.Add(time.Minute) // Ninja is open interval, need to get the exact timestamp, too
		req.Where = fmt.Sprintf("sorigin.eq.%s,sactive.eq.true,mperiod.eq.86400,pcode.eq.%s", origin, parId)
		req.Limit = -1

		res := &ninja.NinjaResponse[[]struct {
			Tstamp ninja.NinjaTime `json:"_timestamp"`
			DType  string          `json:"tname"`
			Value  uint64          `json:"mvalue"`
		}]{}

		err := ninja.History(req, res)
		if err != nil {
			slog.Error("sumParent: Error in ninja call. aborting", "err", err)
			return
		}

		sums := make(map[string]map[time.Time]uint64) // datatype / timestamp / sum value

		// build sums per datatype and timestamp (should be full days)
		for _, m := range res.Data {
			if _, exists := sums[m.DType]; !exists {
				sums[m.DType] = make(map[time.Time]uint64)
			}
			sums[m.DType][m.Tstamp.Time] = sums[m.DType][m.Tstamp.Time] + m.Value
		}

		recs := bdplib.DataMap{}
		for dType, times := range sums {
			for timestamp, value := range times {
				recs.AddRecord(parId, dType, bdplib.CreateRecord(timestamp.UnixMilli(), value, periodAggregate))
			}
		}
		bdplib.PushData(parentStationType, recs)
	}
}
