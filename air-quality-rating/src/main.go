// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"context"
	"log/slog"
	"maps"
	"slices"
	"strconv"
	"strings"
	"time"

	"github.com/noi-techpark/go-bdp-client/bdplib"
	"github.com/noi-techpark/go-timeseries-client/odhts"
	"github.com/noi-techpark/go-timeseries-client/where"
	"github.com/noi-techpark/opendatahub-go-sdk/ingest/ms"
	"github.com/noi-techpark/opendatahub-go-sdk/tel"
	"github.com/robfig/cron/v3"
)

var env struct {
	LOG_LEVEL         string
	CRON              string
	NINJA_BASEURL     string
	NINJA_REFERER     string
	ODH_TOKEN_URL     string
	ODH_CLIENT_ID     string
	ODH_CLIENT_SECRET string
}

func main() {
	ms.InitWithEnv(context.Background(), "", &env)
	slog.Info("Starting air-quality-rating elaboration...")
	defer tel.FlushOnPanic()

	// b := bdplib.FromEnv()

	n := odhts.NewCustomClient(env.NINJA_BASEURL, env.ODH_TOKEN_URL, "el-air-quality-rating")
	n.UseAuth(env.ODH_CLIENT_ID, env.ODH_CLIENT_SECRET)

	c := cron.New(cron.WithSeconds())
	c.AddFunc(env.CRON, func() {

	})
}

type Elaboration struct {
	StationTypes        []string
	Filter              string
	OnlyActiveStations  bool
	BaseTypes           []BaseDataType
	ElaboratedTypes     []ElaboratedDataType
	StartingPoint       time.Time
	b                   *bdplib.Bdp
	c                   *odhts.C
	timeBatchAdder      historyTimeBatcher
	HistoryRequestLimit int
}

type historyTimeBatcher = func(time.Time) time.Time

// arbitraty starting point where there should be no data yet
var minTime = time.Date(2010, 1, 1, 0, 0, 0, 0, time.UTC)

func NewElaboration(ts *odhts.C, bdp *bdplib.Bdp) Elaboration {
	return Elaboration{b: bdp, c: ts, timeBatchAdder: oneMonth, HistoryRequestLimit: 1000, StartingPoint: minTime}
}

type BaseDataType struct {
	Name   string
	Period Period
}

type ElaboratedDataType struct {
	Name        string
	Period      Period
	Unit        string
	Description string
	Rtype       string
	MetaData    map[string]any
	DontSync    bool
}

func (e Elaboration) SyncDataTypes() []bdplib.DataTypeList {
	return []bdplib.DataTypeList{}
}

type Station struct {
	Stationcode string `json:"scode"`
	Name        string `json:"sname"`
	Origin      string `json:"sorigin"`
	Stationtype string `json:"stype"`
	Coord       struct {
		X    float32
		Y    float32
		Srid uint32
	} `json:"scoordinate"`
	Metadata map[string]any `json:"smetadata"`
}

type Measurement odhts.LatestDto
type Period = uint64

func (e Elaboration) GetInitialState() (ElaborationState, error) {
	req := e.buildInitialStateRequest()

	var res odhts.Response[DtoTreeData]
	err := odhts.Latest(*e.c, req, &res)
	if err != nil {
		slog.Error("error getting latest records from ninja. aborting...", "err", err)
		return ElaborationState{}, err
	}

	return mapNinja2ElabTree(res), nil
}

func (e Elaboration) buildInitialStateRequest() *odhts.Request {
	req := odhts.DefaultRequest()
	req.Repr = odhts.TreeNode
	req.StationTypes = e.StationTypes

	datatypes := map[string]struct{}{}
	periods := map[string]struct{}{}
	for _, t := range e.BaseTypes {
		datatypes[t.Name] = struct{}{}
		periods[strconv.FormatUint(t.Period, 10)] = struct{}{}
	}
	for _, t := range e.ElaboratedTypes {
		datatypes[t.Name] = struct{}{}
		periods[strconv.FormatUint(t.Period, 10)] = struct{}{}
	}

	req.DataTypes = slices.Collect(maps.Keys(datatypes))
	periodsStr := strings.Join(slices.Collect(maps.Keys(periods)), ",")

	filters := []string{}
	if e.OnlyActiveStations {
		filters = append(filters, where.Eq("sactive", "true"))
	}
	if periodsStr != "" {
		filters = append(filters, where.In("mperiod", periodsStr))
	}
	if e.Filter != "" {
		filters = append(filters, e.Filter)
	}
	if len(filters) > 0 {
		req.Where = where.And(filters...)
	}

	req.Limit = -1
	return req
}

func mapNinja2ElabTree(o odhts.Response[DtoTreeData]) ElaborationState {
	// Tree is the same stationtype / stationcode / datatype structure
	e := ElaborationState{}
	for k, v := range o.Data {
		stype := ESStationType{}
		stype.Stations = map[string]ESStation{}
		for k, v := range v.Stations {
			st := ESStation{}
			st.Station = v.Station
			st.Datatypes = map[string]ESDataType{}
			for k, v := range v.Datatypes {
				dt := ESDataType{}
				dt.Periods = map[Period]time.Time{}
				for _, m := range v.Measurements {
					// since this is supposed to be a /latest request, periods are assumed to be unique
					dt.Periods[Period(m.Period)] = m.Time.Time
				}
				st.Datatypes[k] = dt
			}
			stype.Stations[k] = st
		}
		e[k] = stype
	}

	return e
}

type ESStationType struct {
	Stations map[string]ESStation
}

type ESStation struct {
	Station   Station
	Datatypes map[string]ESDataType
}

type ESDataType struct {
	Periods map[Period]time.Time
}

type ElaborationState = map[string]ESStationType

func oneMonth(t time.Time) time.Time {
	return t.AddDate(0, 1, 0)
}

func (e Elaboration) GetHistory(stationtypes []string, stationcodes []string, datatypes []string, periods []Period, from time.Time, to time.Time) ([]Measurement, error) {
	var ret []Measurement

	// Ninja cannot handle too large time period requests, so we do it one month at a time
	for start, end := from, to; start.Before(end); start = e.timeBatchAdder(start) {
		windowEnd := e.timeBatchAdder(start)
		if windowEnd.After(end) {
			windowEnd = end
		}
		for page := 0; ; page += 1 {
			req := e.buildHistoryRequest(stationtypes, stationcodes, datatypes, periods, from, to)

			req.Select = "mvalue,mperiod,mvalidtime,scode,stype,tname"
			req.Limit = e.HistoryRequestLimit
			req.Offset = uint(page * req.Limit)

			res := &odhts.Response[[]Measurement]{}

			err := odhts.History(*e.c, req, res)
			if err != nil {
				return nil, err
			}

			ret = append(ret, res.Data...)

			// only if limit = length, there might be more data
			if res.Limit != int64(len(res.Data)) {
				break
			} else {
				slog.Debug("Using pagination to request more data: ", "limit", res.Limit, "data.length", len(res.Data), "offset", req.Offset, "firstDate", res.Data[0].MValidTime.Time)
			}
		}
	}
	return ret, nil
}
func (e Elaboration) buildHistoryRequest(stationtypes []string, stationcodes []string, datatypes []string, periods []Period, from time.Time, to time.Time) *odhts.Request {
	req := odhts.DefaultRequest()
	req.Repr = odhts.FlatNode
	req.StationTypes = stationtypes
	req.From = from
	req.To = to

	req.DataTypes = datatypes

	periodsStr := []string{}
	for _, period := range periods {
		periodsStr = append(periodsStr, strconv.FormatUint(period, 10))
	}

	filters := []string{}
	if e.OnlyActiveStations {
		filters = append(filters, where.Eq("sactive", "true"))
	}
	if len(periodsStr) > 0 {
		filters = append(filters, where.In("mperiod", periodsStr...))
	}
	if len(stationcodes) > 0 {
		filters = append(filters, where.In("scode", where.EscapeList(stationcodes...)...))
	}
	if e.Filter != "" {
		filters = append(filters, e.Filter)
	}
	if len(filters) > 0 {
		req.Where = where.And(filters...)
	}

	req.Limit = -1
	return req
}

// we find the earlieast derived type (e.g. the end of)
func (e Elaboration) StationCatchupInterval(s ESStation) (from time.Time, to time.Time) {
	for _, t := range e.BaseTypes {
		edt := s.Datatypes[t.Name]
		if edt.Periods != nil {
			per := edt.Periods[t.Period]
			if to.Before(per) {
				to = per
			}
		}
	}
	for _, t := range e.ElaboratedTypes {
		edt := s.Datatypes[t.Name]
		if edt.Periods != nil {
			per := edt.Periods[t.Period]
			if from.IsZero() || from.After(per) {
				from = per
			}
		}
	}
	if from.IsZero() {
		from = e.StartingPoint
	}
	return
}

func (e Elaboration) getStationInterval(s ESStation, from time.Time, to time.Time) ([]Measurement, error) {
	dts := []string{}
	periods := []Period{}
	for _, t := range e.BaseTypes {
		dts = append(dts, t.Name)
		periods = append(periods, t.Period)
	}
	return e.GetHistory([]string{s.Station.Stationtype}, []string{s.Station.Stationcode}, dts, periods, from, to)
}

/*
Elaborate one station at a time, catch up from earlierst elaborated measurement to latest base measurement.
*/
func (e Elaboration) FollowStation(es ElaborationState, handle func(Station, []Measurement) ([]ElabResult, error)) {
	for stationtype, stp := range es {
		for _, st := range stp.Stations {
			from, to := e.StationCatchupInterval(st)
			if !to.After(from) {
				// No data or already caught up
				slog.Debug("not computing anything for station", "station", st)
				continue
			}
			ms, err := e.getStationInterval(st, from, to)
			if err != nil {
				slog.Error("failed requesting data for station. continuing...", "station", st, "err", err, "from", from, "to", to)
				continue
			}
			res, err := handle(st.Station, ms)
			if err != nil {
				slog.Error("error during elaboration of station. continuing...", "station", st, "err", err, "from", from, "to", to)
				continue
			}
			if err := e.PushResults(stationtype, res); err != nil {
				slog.Error("error pushing result for station", "station", st, "err", err, "from", from, "to", to)
				continue
			}
		}
	}
}
func (e Elaboration) PushResults(stationtype string, results []ElabResult) error {
	b := (*e.b)
	dm := b.CreateDataMap()
	for _, r := range results {
		dm.AddRecord(r.StationCode, r.DataType, bdplib.CreateRecord(r.Timestamp.UnixMilli(), r.Value, r.Period))
	}
	return b.PushData(stationtype, dm)
}

type ElabResult struct {
	Timestamp   time.Time
	Period      Period
	StationType string
	StationCode string
	DataType    string
	Value       any
}

type DtoMeasurement struct {
	Period uint64       `json:"mperiod"`
	Time   odhts.TsTime `json:"mvalidtime"`
	Since  odhts.TsTime `json:"mtransactiontime"`
}

type DtoTreeData = map[string]struct {
	Stations map[string]struct {
		Station
		Datatypes map[string]struct {
			Measurements []DtoMeasurement `json:"tmeasurements"`
		} `json:"sdatatypes"`
	} `json:"stations"`
}
