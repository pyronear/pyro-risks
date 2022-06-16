# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

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
