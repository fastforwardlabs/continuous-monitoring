import numpy as np
import pandas as pd

from pandas.tseries.offsets import DateOffset

def random_day_offset(ts: pd._libs.tslibs.timestamps.Timestamp, max_days=60):
    """
    Given a pandas Timestamp, return a new timestep offset to an earlier date by
    a random number of days between 0 and max_days.
    """
    return ts - DateOffset(np.random.randint(0, max_days))