# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from typing import Tuple
import pandas as pd

__all__ = ["check_xy", "check_x", "discretizer"]


def check_xy(X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Validate inputs for transformers.

    Args:
        X: Training dataset features pd.DataFrame.
        y: Training dataset target pd.Series.

    Raises:
        TypeError: Transformer methods expect pd.DataFrame and pd.Series as inputs.

    Returns:
        Copy of the inputs.
    """
    if isinstance(X, pd.DataFrame) and isinstance(y, pd.Series):
        X = X.copy()
        y = y.copy()
    else:
        raise TypeError(
            "Transformer methods expect pd.DataFrame\
                and pd.Series as inputs."
        )
    return X, y


def check_x(X: pd.DataFrame) -> pd.DataFrame:
    """
    Validate inputs for tranformers.

    Args:
        X: Training dataset features pd.DataFrame.

    Raises:
        TypeError: Transformer methods expect pd.DataFrame as inputs.

    Returns:
        Copy of the inputs.
    """
    if isinstance(X, pd.DataFrame):
        X = X.copy()
    else:
        raise TypeError("Transformer methods expect pd.DataFrame as inputs")
    return X


def discretizer(x: float) -> int:
    """
    Discretize values.

    Args:
        x (float): value to be discretized

    Returns:
        int: discretized value
    """
    return 1 if x > 0 else 0


def lagged_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds columns to the original dataframe with 1, 3 and 7 days lags.

    Args:
        df (pd.DataFrame): DataFrame to lag, for one department and one feature only.

    Returns:
        pd.DataFrame: Lagged dataframe.
    """
    lagged_aggregated_df = df.copy()

    lagged_aggregated_df = lagged_aggregated_df.join(
        df.shift(periods=1, freq="D"), rsuffix="_lag1", how="left"
    )

    lagged_aggregated_df = lagged_aggregated_df.join(
        df.shift(periods=3, freq="D"), rsuffix="_lag3", how="left"
    )

    lagged_aggregated_df = lagged_aggregated_df.join(
        df.shift(periods=7, freq="D"), rsuffix="_lag7", how="left"
    )
    return lagged_aggregated_df
