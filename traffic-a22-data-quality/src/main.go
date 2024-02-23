// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"log/slog"
	"os"
	"time"
	"traffic-a22-data-quality/dc"
	"traffic-a22-data-quality/log"

	"github.com/go-co-op/gocron"
)

func main() {
	log.InitLogger()

	cron := os.Getenv("SCHEDULER_CRON")
	slog.Debug("Cron defined as: " + cron)

	if len(cron) == 0 {
		slog.Error("Cron job definition in env missing")
		os.Exit(1)
	}

	dc.Job()
	s := gocron.NewScheduler(time.UTC)
	s.CronWithSeconds(cron).Do(dc.Job)
	s.StartBlocking()
}
