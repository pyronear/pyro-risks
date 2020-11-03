import pandas as pd


def get_intersection_range(ts1: pd.Series, ts2: pd.Series) -> pd.DatetimeIndex:
    """Computes the intersecting date range of two series

    Args:
        ts1: time series
        ts2: time series
    """

    # Time span selection
    time_range1 = max(ts1.min(), ts2.min())
    time_range2 = min(ts1.max(), ts2.max())
    if time_range1 > time_range2:
        raise ValueError("Extracts do not have intersecting date range")

    return pd.date_range(time_range1, time_range2)
