// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"strings"
	"time"

	"github.com/noi-techpark/go-bdp-client/bdplib"
	"github.com/noi-techpark/go-timeseries-client/odhts"
	"github.com/noi-techpark/go-timeseries-client/where"
	"github.com/noi-techpark/opendatahub-go-sdk/ingest/ms"
	"github.com/noi-techpark/opendatahub-go-sdk/tel"
	"github.com/robfig/cron/v3"
)

func Ptr[T any](v T) *T {
	return &v
}

var env struct {
	LOG_LEVEL         string
	CRON              string
	TS_API_BASE_URL   string
	TS_API_REFERER    string
	ODH_TOKEN_URL     string
	ODH_CLIENT_ID     string
	ODH_CLIENT_SECRET string
}

func main() {
	ms.InitWithEnv(context.Background(), "", &env)
	slog.Info("Starting dataset-watcher elaboration...")
	defer tel.FlushOnPanic()

	b := bdplib.FromEnv(bdplib.BdpEnv{
		BDP_BASE_URL:           os.Getenv("BDP_BASE_URL"),
		BDP_PROVENANCE_VERSION: os.Getenv("BDP_PROVENANCE_VERSION"),
		BDP_PROVENANCE_NAME:    os.Getenv("BDP_PROVENANCE_NAME"),
		BDP_ORIGIN:             os.Getenv("BDP_ORIGIN"),
		BDP_TOKEN_URL:          os.Getenv("ODH_TOKEN_URL"),
		BDP_CLIENT_ID:          os.Getenv("ODH_CLIENT_ID"),
		BDP_CLIENT_SECRET:      os.Getenv("ODH_CLIENT_SECRET"),
	})

	n := odhts.NewCustomClient(env.TS_API_BASE_URL, env.ODH_TOKEN_URL, env.TS_API_REFERER)
	n.UseAuth(env.ODH_CLIENT_ID, env.ODH_CLIENT_SECRET)

	job := func() {
		slog.Info("Starting watch pass run")
		// get rules
		// cycle rules
		for _, rule := range rules() {
			var err error
			switch rule.Type {
			case RULE_TYPE_AGE:
				err = handleRuleAge(context.Background(), n, b, &rule)
			default:
				ms.FailOnError(context.Background(), fmt.Errorf("unrecognized rule type"), "type", rule.Type)
			}

			ms.FailOnError(context.Background(), err, "rule failed")
		}
	}

	job()
	c := cron.New(cron.WithSeconds())
	c.AddFunc(env.CRON, job)
	c.Start()
	select {}
}

type RuleType string

const (
	RULE_TYPE_AGE = "AGE"
)

type Rule struct {
	StationType string
	Origin      *string
	Type        RuleType
	Params      any
}

type RuleParamsAge struct {
	MaxAge            time.Duration
	ReferenceDataType string
}

func rules() []Rule {
	return []Rule{
		{StationType: "ParkingSensor", Origin: Ptr("systems"), Type: RULE_TYPE_AGE, Params: RuleParamsAge{MaxAge: 604800 * time.Second, ReferenceDataType: "free"}},
	}
}

func getStations(tsClient odhts.C, rule *Rule) ([]string, error) {
	type DtoStationData = []struct {
		Stationcode string `json:"scode"`
	}

	req := odhts.DefaultRequest()
	req.Repr = odhts.FlatNode
	req.StationTypes = []string{rule.StationType}
	if rule.Origin != nil {
		req.Where = where.Eq("sorigin", *rule.Origin)
	}
	req.Select = "scode"
	req.Limit = -1

	var res odhts.Response[DtoStationData]
	err := odhts.StationType(tsClient, req, &res)
	if err != nil {
		return nil, err
	}

	stationCodes := []string{}
	for _, s := range res.Data {
		stationCodes = append(stationCodes, s.Stationcode)
	}

	return stationCodes, nil
}

type DtoLatestData = []struct {
	Time        NinjaTime `json:"mvalidtime"`
	Stationcode string    `json:"scode"`
}

type NinjaTime struct {
	time.Time
}

func (nt *NinjaTime) UnmarshalJSON(b []byte) (err error) {
	s := strings.Trim(string(b), "\"")
	if s == "null" {
		nt.Time = time.Time{}
		return
	}
	nt.Time, err = time.Parse("2006-01-02 15:04:05.000-0700", s)
	return
}

func getLatest(tsClient odhts.C, rule *Rule, types []string) (DtoLatestData, error) {
	req := odhts.DefaultRequest()
	req.Repr = odhts.FlatNode
	req.DataTypes = types
	req.StationTypes = []string{rule.StationType}
	if rule.Origin != nil {
		req.Where = where.Eq("sorigin", *rule.Origin)
	}
	req.Select = "scode,mvalidtime"
	req.Limit = -1

	var res odhts.Response[DtoLatestData]
	err := odhts.Latest(tsClient, req, &res)
	if err != nil {
		return nil, err
	}

	return res.Data, nil
}

func handleRuleAge(ctx context.Context, tsClient odhts.C, b bdplib.Bdp, rule *Rule) error {
	slog.Debug("Elaborating rule Age", "stationtype", rule.StationType, "origin", rule.Origin)
	params, ok := rule.Params.(RuleParamsAge)
	if !ok {
		return fmt.Errorf("unrecognized rule age parameters")
	}

	// get stations
	stations, err := getStations(tsClient, rule)
	if err != nil {
		return err
	}

	// get latest
	latest, err := getLatest(tsClient, rule, []string{params.ReferenceDataType})
	if err != nil {
		return err
	}
	latestLookup := map[string]time.Time{}
	for _, l := range latest {
		latestLookup[l.Stationcode] = l.Time.Time
	}

	activeStations := []string{}
	for _, s := range stations {
		lastTime, ok := latestLookup[s]
		if ok && time.Since(lastTime) < params.MaxAge {
			activeStations = append(activeStations, s)
		}
	}

	// change state

	return b.SyncStationStates(rule.StationType, rule.Origin, activeStations, false)
}
