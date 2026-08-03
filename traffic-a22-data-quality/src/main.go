// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"log/slog"
	"os"
	"traffic-a22-data-quality/dc"
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

	// scheduling is handled externally by a Kubernetes CronJob
	if err := dc.Job(); err != nil {
		slog.Error("job failed", "err", err)
		os.Exit(1)
	}
}
