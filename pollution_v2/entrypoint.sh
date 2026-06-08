#!/bin/sh
# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# If CRON_SCHEDULE is set the job runs on that schedule via supercronic.
# Otherwise the command is executed once and the container exits.

set -e

if [ -n "${CRON_SCHEDULE}" ]; then
    echo "${CRON_SCHEDULE} $*" > /tmp/job.crontab
    exec supercronic /tmp/job.crontab
else
    exec "$@"
fi
