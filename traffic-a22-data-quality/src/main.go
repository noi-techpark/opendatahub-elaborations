// SPDX-FileCopyrightText: (c) NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"traffic-a22-data-quality/dc"
	"traffic-a22-data-quality/log"
)

func main() {
	log.InitLogger()

	/* cron := os.Getenv("SCHEDULER_CRON")
	slog.Debug("Cron defined as: " + cron)

	if len(cron) == 0 {
		slog.Error("Cron job definition in env missing")
		os.Exit(1)
	} */

	dc.Job()
	// start cron job
	// s := gocron.NewScheduler(time.UTC)
	// s.CronWithSeconds(cron).Do(dc.Job)
	// s.StartBlocking()
}
