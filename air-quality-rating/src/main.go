// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"log/slog"
	"os"
	"time"
	"traffic-a22-data-quality/dc"

	"github.com/go-co-op/gocron/v2"
)

// read logger level from env and uses INFO as default
func initLogging() {
	logLevel := os.Getenv("LOG_LEVEL")

	level := new(slog.LevelVar)
	level.UnmarshalText([]byte(logLevel))

	slog.SetDefault(slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: level,
	})))

	slog.Info("Start logger with level: " + logLevel)
}

func main() {
	initLogging()

	cron := os.Getenv("SCHEDULER_CRON")
	slog.Debug("Cron defined as: " + cron)

	if len(cron) == 0 {
		slog.Error("Cron job definition in env missing")
		os.Exit(1)
	}

	dc.Job()
	s, err := gocron.NewScheduler(gocron.WithLocation(time.UTC))
	if err != nil {
		panic(err)
	}
	s.NewJob(gocron.CronJob(cron, true), gocron.NewTask(dc.Job))
	s.Start()
	select {}
}
