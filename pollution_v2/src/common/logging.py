# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import logging.config

from common.settings import LOG_LEVEL, LOG_LEVEL_LIBS


def setup_logging(service_name: str) -> None:
    """Configure JSON structured logging for the given service."""
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.json.JsonFormatter",
                "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "rename_fields": {"asctime": "timestamp", "levelname": "level"},
                "static_fields": {"service": service_name},
            }
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {
            "level": LOG_LEVEL,
            "handlers": ["stdout"],
        },
        "loggers": {
            "urllib3": {"level": LOG_LEVEL_LIBS, "propagate": True},
            "requests": {"level": LOG_LEVEL_LIBS, "propagate": True},
            "keycloak": {"level": LOG_LEVEL_LIBS, "propagate": True},
        },
    })
