import os
import sklearn
import numpy as np
import pandas as pd
from datetime import datetime
from pandas.tseries.offsets import DateOffset
from sklearn.preprocessing import FunctionTransformer

def random_day_offset(ts: pd._libs.tslibs.timestamps.Timestamp, max_days=60):
    """
    Given a pandas Timestamp, return a new timestep offset to an earlier date by
    a random number of days between 0 and max_days.
    """
    return ts - DateOffset(np.random.randint(0, max_days))


def get_active_feature_names(
    column_transformer,
):
    """Inspect the transformer steps in a given sklearn.ColumnTransformer to collect and
    return the names of all features that are not dropped as part of the pipeline."""

    active_steps = [
        k for k, v in column_transformer.named_transformers_.items() if v != "drop"
    ]

    return np.concatenate(
        [column_transformer.named_transformers_[step].feature_names_in_ for step in active_steps]
    ).tolist()

def outlier_removal(X, multiple, cols):
    """
    Replaces outliers in each column of a pd.DataFrame with np.Nan values.

    Outlier strictness is controlled by multiples of the IQR from each quantile.
    """

    X = pd.DataFrame(X).copy()

    for col in cols:

        x = pd.Series(X.loc[:, col]).copy()
        q1 = x.quantile(0.25)
        q3 = x.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - (multiple * iqr)
        upper = q3 + (multiple * iqr)

        X.loc[~X.loc[:, col].between(lower, upper, inclusive=True), col] = np.nan

    return X[~X.isna().any(axis=1)]


def scale_prices(df):
    """
    Scale prices from being denominated in dollars to hundreds of thousands of dollars.
    """
    copy = df.copy(deep=True)
    for col in ("ground_truth", "predicted_result"):
        copy[col] = copy[col] / 100_000

    return copy


def find_latest_report(report_dir):
    """
    Use date prefixed report titles located in a provided report_dir to identify the
    latest report and return the filename.

    Filename date prefixes should be in the format: "%Y-%m-%d"

    """
    reports = os.listdir(report_dir)
    date_map = {report.split("_")[0]: i for i, report in enjumerate(reports) if report.split('.')[-1]=='html'}
    latest_report = max(date_map.keys(), key=lambda d: datetime.strptime(d, "%Y-%m-%d"))

    return reports[date_map[latest_report]]










