# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import argparse
import logging.config

import dateutil.parser
import sentry_sdk
from celery.result import AsyncResult

from pollution_connector.common.logging import get_logging_configuration
from common.settings import DEFAULT_TIMEZONE, SENTRY_SAMPLE_RATE
from pollution_connector.tasks.pollution_computation import compute_pollution_data

logging.config.dictConfig(get_logging_configuration("pollution_v2_connector"))
logger = logging.getLogger("pollution_v2_connector")

sentry_sdk.init(
    traces_sample_rate=SENTRY_SAMPLE_RATE,
    integrations=[]
)

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description="Manually run a pollution (v2) computation")
    arg_parser.add_argument("-f", "--from-date", type=str, required=False,
                            help="The starting date[time] in isoformat (up to one second level of precision, milliseconds for the from date field are not supported in ODH) for downloading data from ODH if no pollution measures are available")

    arg_parser.add_argument("-t", "--to-date", type=str, required=False,
                            help="The end date[time] in isoformat for downloading the traffic measures. If not specified, the default will be the current datetime")

    arg_parser.add_argument("--run-async", action="store_true", help="If set it run the task in the celery cluster")
    args = arg_parser.parse_args()

    if args.from_date:
        from_date = dateutil.parser.parse(args.from_date)
        if from_date.tzinfo is None:
            from_date = DEFAULT_TIMEZONE.localize(from_date)
        if from_date.microsecond:
            from_date = from_date.replace(microsecond=0)
    else:
        from_date = None

    if args.to_date:
        to_date = dateutil.parser.parse(args.to_date)
        if to_date.tzinfo is None:
            to_date = DEFAULT_TIMEZONE.localize(to_date)
    else:
        to_date = None

    compute_pollution_data(min_from_date=from_date, max_to_date=to_date)
    '''if args.run_async:
        task: AsyncResult = compute_pollution_data.delay(min_from_date=from_date, max_to_date=to_date)
        logger.info(f"Scheduled async pollution computation. Task ID: [{task.task_id}]")
    else:
        logger.info("Staring pollution computation")
        compute_pollution_data(min_from_date=from_date, max_to_date=to_date)'''
