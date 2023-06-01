# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging

from celery.schedules import crontab

from pollution_connector.celery_configuration.celery_app import app
from pollution_connector.settings import POLLUTION_TASK_SCHEDULING_MINUTE, POLLUTION_TASK_SCHEDULING_HOUR
from pollution_connector.tasks.pollution_computation import compute_pollution_data


logger = logging.getLogger("pollution_connector.celery_configuration.periodic_tasks")


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info("Setup periodic tasks")
    sender.add_periodic_task(
        crontab(
            minute=POLLUTION_TASK_SCHEDULING_MINUTE,
            hour=POLLUTION_TASK_SCHEDULING_HOUR
        ),
        compute_pollution_data.s(),
        name='compute pollution data every 10'
    )
