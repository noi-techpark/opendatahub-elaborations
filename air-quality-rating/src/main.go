// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"context"
	"fmt"
	"log/slog"
	"maps"
	"slices"
	"strconv"
	"strings"
	"time"

	"github.com/noi-techpark/go-bdp-client/bdplib"
	"github.com/noi-techpark/go-timeseries-client/odhts"
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
	StationTypes       []string
	Filter             string
	OnlyActiveStations bool
	BaseTypes          []BaseDataType
	DerivedTypes       []DerivedDataType
	b                  *bdplib.Bdp
	c                  *odhts.C
}

func NewElaboration(ts *odhts.C, bdp *bdplib.Bdp) Elaboration {
	return Elaboration{b: bdp, c: ts}
}

type BaseDataType struct {
	Name   string
	Period Period
}

type DerivedDataType struct {
	Name        string
	Unit        string
	Description string
	Rtype       string
	Period      Period
	MetaData    map[string]any
	DontSync    bool
}

func (e Elaboration) SyncDataTypes() []bdplib.DataTypeList {
	return []bdplib.DataTypeList{}
}

type Station odhts.StationDto[map[string]any]
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
	for _, t := range e.DerivedTypes {
		datatypes[t.Name] = struct{}{}
		periods[strconv.FormatUint(t.Period, 10)] = struct{}{}
	}

	req.DataTypes = slices.Collect(maps.Keys(datatypes))
	periodsStr := strings.Join(slices.Collect(maps.Keys(periods)), ",")

	filters := []string{}
	if e.OnlyActiveStations {
		filters = append(filters, "sactive.eq.true")
	}
	if periodsStr != "" {
		filters = append(filters, fmt.Sprintf("mperiod.in.(%s)", periodsStr))
	}
	if e.Filter != "" {
		filters = append(filters, e.Filter)
	}
	if len(filters) > 0 {
		req.Where = fmt.Sprintf("and(%s)", strings.Join(filters, ","))
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

func (e Elaboration) GetHistory(stationtype string, stationcode string, datatype string, period Period, filter string, from time.Time, to time.Time) ([]Measurement, error) {
	return []Measurement{}, nil
}

func (e Elaboration) FollowStation(es ElaborationState, handle func(Station, []Measurement) ([]ElabResult, error)) {
	for _, stp := range es {
		for _, st := range stp.Stations {
			handle(st.Station, []Measurement{})
		}
	}
}

func (e Elaboration) PushResults(results []ElabResult) error {
	return nil
}

type ElabResult struct {
	Timestamp   int64
	Period      Period
	StationType string
	StationCode string
	DataType    string
	Value       interface{}
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
