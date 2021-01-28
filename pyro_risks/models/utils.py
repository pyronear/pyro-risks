from typing import List, Union, Optional, Dict, Tuple
import pandas as pd
import numpy as np

__all__ = ["check_xy", "check_x"]


def check_xy(X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
    """Validate inputs for transformers.

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
        raise TypeError('Transformer methods expect pd.DataFrame\
                and pd.Series as inputs.')
    return X, y


def check_x(X: pd.DataFrame) -> pd.DataFrame:
    """Validate inputs for tranformers.

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
        raise TypeError('Transformer methods expect pd.DataFrame as inputs')
    return X
