// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package dc

import (
	"fmt"
	"log/slog"
	"time"
	"traffic-a22-data-quality/ninja"

	"github.com/noi-techpark/go-bdp-client/bdplib"
	"golang.org/x/exp/maps"
)

func sumParentJob() {
	req := ninja.DefaultNinjaRequest()
	req.DataTypes = append(maps.Keys(aggrDataTypes), TotalType.Name)
	req.Select = "tname,mvalue,pcode,stype,scode"
	req.Where = fmt.Sprintf("sorigin.eq.%s,sactive.eq.true,mperiod.eq.%d", origin, periodAgg)
	req.Limit = -1

	res := &ninja.NinjaResponse[[]struct {
		Tstamp  ninja.NinjaTime `json:"_timestamp"`
		DType   string          `json:"tname"`
		Value   float64         `json:"mvalue"`
		Parent  string          `json:"pcode"`
		Station string          `json:"scode"`
		Stype   string          `json:"stype"`
	}]{}

	err := ninja.Latest(req, res)
	if err != nil {
		slog.Error("sumParent: Error in ninja call. aborting", "err", err)
		panic(err)
	}

	type window = struct {
		from time.Time
		to   time.Time
	}

	// parentId / datatype
	parents := make(map[string]map[string]window)

	// For each parent/type find out where the elaboration window starts/ends
	for _, m := range res.Data {
		parentStationCode := m.Parent
		// type is parent station, the code we are targeting is m.stationcode
		if m.Stype == parentStationType {
			parentStationCode = m.Station
		}

		if _, exists := parents[parentStationCode]; !exists {
			parents[parentStationCode] = make(map[string]window)
		}

		t := parents[parentStationCode][m.DType]
		// There is only one parent record per data type
		if m.Stype == parentStationType {
			t.from = m.Tstamp.Time
		} else {
			if m.Tstamp.Time.After(t.to) {
				t.to = m.Tstamp.Time
			}
		}
		parents[parentStationCode][m.DType] = t
	}

	for parId, types := range parents {
		// Do only a single request per parent. So we determine the max window.
		// Note that when a data type does not exist yet on parent station, but in a child station, the window defaults to from = 0000-00-00...
		var from time.Time
		var to time.Time
		for _, tp := range types {
			if (!tp.from.IsZero() && from.IsZero()) || tp.from.Before(from) {
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
		req.Where = fmt.Sprintf("sorigin.eq.%s,sactive.eq.true,mperiod.eq.86400,pcode.eq.\"%s\"", origin, parId)
		req.Limit = -1

		res := &ninja.NinjaResponse[[]struct {
			Tstamp ninja.NinjaTime `json:"_timestamp"`
			DType  string          `json:"tname"`
			Value  float64         `json:"mvalue"`
		}]{}

		err := ninja.History(req, res)
		if err != nil {
			slog.Error("sumParent: Error in ninja call. aborting", "err", err)
			panic(err)
		}

		sums := make(map[string]map[time.Time]float64) // datatype / timestamp / sum value

		// build sums per datatype and timestamp (should be full days)
		for _, m := range res.Data {
			if _, exists := sums[m.DType]; !exists {
				sums[m.DType] = make(map[time.Time]float64)
			}
			sums[m.DType][m.Tstamp.Time] = sums[m.DType][m.Tstamp.Time] + m.Value
		}

		recs := bdp.CreateDataMap()
		for dType, times := range sums {
			for timestamp, value := range times {
				recs.AddRecord(parId, dType, bdplib.CreateRecord(timestamp.UnixMilli(), value, periodAgg))
			}
		}
		bdp.PushData(parentStationType, recs)
	}
}
