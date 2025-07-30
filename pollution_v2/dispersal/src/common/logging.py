# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os

from dotenv import load_dotenv

from common.settings import LOGS_DIR, LOG_LEVEL, LOG_LEVEL_LIBS

# Load .env file
load_dotenv()

log_level = LOG_LEVEL
log_level_libraries = LOG_LEVEL_LIBS

log_handlers = ["console"]
if "LOG_TO_FILE" in os.environ:
    log_handlers.append("file")


def get_logging_configuration(service_name: str):
    """
    Get the logging configuration to be associated to a particular service.

    :param service_name: The name of the service (e.g. ws, backend, rule-engine, ..)
    :return: The logging configuration
    """
    file_name = f"{service_name}.log"

    log_config = {
        "version": 1,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": ""
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "simple",
                "filename": os.path.join(LOGS_DIR, file_name),
                "maxBytes": 10485760,
                "backupCount": 3
            }
        },
        "root": {
            "level": log_level,
            "handlers": log_handlers,
        },
        "loggers": {
            "werkzeug": {
                "level": log_level_libraries,
                "handlers": log_handlers,
                "propagate": 0
            },
            "uhopper": {
                "level": log_level,
                "handlers": log_handlers,
                "propagate": 0
            },
            "pollution_v2": {
                "level": log_level,
                "handlers": log_handlers,
                "propagate": 0
            },
        }
    }

    return log_config
