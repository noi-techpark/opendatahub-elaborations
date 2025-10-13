# SPDX-FileCopyrightText: 2021-2025 STA AG <info@sta.bz.it>
# SPDX-FileContributor: Chris Mair <chris@1006.org>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np
import pandas as pd

def onehot(val, categories):
    ret = np.zeros((1, categories), dtype="float32")
    ret[0, int(val)] = 1
    return ret

def getParkN():
    signals = pd.read_csv("data-predictors/signals.csv", parse_dates=True, nrows=1)
    cnt = 0
    for col in signals.columns:
        if str(col).startswith("occ"):
            cnt += 1
    return cnt
