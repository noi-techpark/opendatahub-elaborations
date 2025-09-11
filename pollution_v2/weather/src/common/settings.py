# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import pytz


MAIN_DIR = os.getenv("MAIN_DIR", "..")
TMP_DIR = f'{MAIN_DIR}/tmp'
DATA_DIR = f'{MAIN_DIR}/data'
PARAMETERS_DIR = f'{DATA_DIR}/parameters'
ROADCAST_DIR = f'{TMP_DIR}/roadcast'
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(PARAMETERS_DIR):
    os.makedirs(PARAMETERS_DIR)
if not os.path.exists(ROADCAST_DIR):
    os.makedirs(ROADCAST_DIR)

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_LEVEL_LIBS = os.getenv("LOG_LEVEL_LIBS", "DEBUG")
LOGS_DIR = os.getenv("LOGS_DIR", "..")

# General
DEFAULT_TIMEZONE = pytz.timezone(os.getenv("DEFAULT_TIMEZONE", "Europe/Rome"))

