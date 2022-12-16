from __future__ import absolute_import, annotations

import logging.config

import sentry_sdk
from celery import Celery
from sentry_sdk.integrations.celery import CeleryIntegration

from pollution_connector.common.logging import get_logging_configuration
from pollution_connector.settings import CELERY_BROKER_URL, CELERY_BACKEND_URL, CELERY_RESULT_EXPIRATION_SECONDS

sentry_sdk.init(
    traces_sample_rate=1.0,
    integrations=[CeleryIntegration()]
)

logging.config.dictConfig(get_logging_configuration("pollution_connector"))
logger = logging.getLogger("pollution_connector")

app = Celery('proj',
             broker=CELERY_BROKER_URL,
             backend=CELERY_BACKEND_URL,
             include=["pollution_connector.celery_configuration.periodic_tasks", "pollution_connector.tasks.pollution_computation"]
             )

app.conf.update(
    result_expires=CELERY_RESULT_EXPIRATION_SECONDS,
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Europe/Oslo',
    enable_utc=True,
)

if __name__ == '__main__':
    app.start()
