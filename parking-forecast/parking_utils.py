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
