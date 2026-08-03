#!/bin/sh

# SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: CC0-1.0
#
# If CRON_SCHEDULE is set the job runs on that schedule via supercronic
# (local dev convenience — see docker-compose.yml). Otherwise the command is
# executed once and the container exits, which is what a Kubernetes CronJob
# relies on in production (see infrastructure/helm).

set -e

if [ -n "${CRON_SCHEDULE}" ]; then
    echo "${CRON_SCHEDULE} $*" > /tmp/job.crontab
    exec supercronic /tmp/job.crontab
else
    exec "$@"
fi
