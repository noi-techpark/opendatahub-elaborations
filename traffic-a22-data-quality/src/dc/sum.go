// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package dc

import (
	"fmt"
	"log/slog"
	"time"
	"traffic-a22-data-quality/bdplib"
	"traffic-a22-data-quality/ninja"

	"golang.org/x/exp/maps"
	"golang.org/x/sync/errgroup"
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

type tv = struct {
	dt time.Time
	v  uint64
}

type rec = struct {
	st string
	t  string
	r  bdplib.Record
}

const numJobs = 5

func sumJob() {
	// Get current elaboration state from ninja. Both where we are with base data and with the sums
	req := ninja.DefaultNinjaRequest()
	req.Repr = ninja.TreeNode
	req.AddStationType(baseStationType)
	req.DataTypes = maps.Keys(aggrDataTypes)
	req.Limit = -1
	req.Select = "mperiod,mvalidtime,pcode"
	req.Where = fmt.Sprintf("and(sactive.eq.true,mperiod.in.(%d,%d))", basePeriod, periodAgg)

	var res ninja.NinjaResponse[NinjaTreeData]
	err := ninja.Latest(req, &res)
	if err != nil {
		slog.Error("error", err)
		return
	}

	stationWindows := requestWindows(res.Data)

	// 	get data history from starting point until last EOD
	for scode, typeMap := range stationWindows {
		total := make(chan tv, 50)
		recs := make(chan rec, 50)
		errs := make(chan error)

		eg := errgroup.Group{}
		eg.SetLimit(numJobs)

		// spin off to worker
		for tname, win := range typeMap {
			tname, win := tname, win // avoid closure over loop variables
			eg.Go(func() error {
				return sumHistory(win, scode, tname, total, recs)
			})
		}

		// wait for all workers to finish
		go func() {
			if err := eg.Wait(); err != nil {
				errs <- err
			}
			close(errs)
			close(total)
		}()

		// capture the single data type sums and make one total
		go func() {
			defer close(recs)

			totals := make(map[time.Time]uint64)
			for t := range total {
				totals[t.dt] += t.v
			}
			for date, total := range totals {
				recs <- rec{scode, TotalType.Name, bdplib.CreateRecord(date.UnixMilli(), total, periodAgg)}
			}
		}()

		bdpMap := bdplib.DataMap{}
		for r := range recs {
			bdpMap.AddRecord(r.st, r.t, r.r)
		}

		if err := <-errs; err != nil {
			slog.Error("Error. Not pushing data", "station", scode, "error", err)
			continue
		}

		bdplib.PushData(baseStationType, bdpMap)
	}
}

func sumHistory(win window, scode string, tname string, total chan tv, recs chan rec) error {
	history, err := getHistoryPaged(win, scode, tname)
	if err != nil {
		slog.Error("Error requesting history data from Ninja", "err", err, "station", scode, "type", tname)
		return err
	}

	sums := make(map[time.Time]uint64)
	for _, m := range history {
		date := stripToDay(m.Timestamp.Time)
		sums[date] = sums[date] + m.Value
		if _, ok := totalDataTypes[tname]; ok {
			total <- tv{date, m.Value}
		}
	}
	for date, sum := range sums {
		recs <- rec{scode, tname, bdplib.CreateRecord(date.UnixMilli(), sum, periodAgg)}
	}
	return nil
}

func getHistoryPaged(todo window, stationCode string, typeName string) ([]NinjaFlatData, error) {
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

func requestWindows(dt NinjaTreeData) map[string]map[string]window {
	todos := make(map[string]map[string]window)
	for _, stations := range dt {
		for stationCode, station := range stations.Stations {
			for tname, dataType := range station.Datatypes {
				for _, m := range dataType.Measurements {
					var firstBase time.Time
					var lastBase time.Time
					var lastAggregate time.Time
					if m.Period == uint64(basePeriod) {
						lastBase = m.Time.Time
						firstBase = m.Since.Time
					}
					if m.Period == periodAgg {
						lastAggregate = m.Time.Time
					}

					// only consider stations that don't have up to date aggregates
					if lastBase.Sub(lastAggregate).Seconds() > periodAgg {
						if _, exists := todos[stationCode]; !exists {
							todos[stationCode] = make(map[string]window)
						}
						todos[stationCode][tname] = window{
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

type window struct {
	firstBase     time.Time
	lastBase      time.Time
	lastAggregate time.Time
}

func getRequestDates(todo window) (time.Time, time.Time) {
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
