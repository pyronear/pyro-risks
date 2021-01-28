from typing import List, Union, Optional, Dict, Tuple
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from .utils import check_xy, check_x
from datetime import datetime

import pandas as pd
import numpy as np


class TargetDiscretizer(BaseEstimator):
    """Discretize numerical target variable.

    The `TargetDiscretizer` transformer maps target variable values to discrete values using
    a user defined function.

    Parameters:
        discretizer: user defined function.
    """

    def __init__(self, discretizer: callable):

        if callable(discretizer):
            self.discretizer = discretizer
        else:
            raise TypeError(f"{self.__class__.__name__} constructor expect a callable")

    def fit_resample(
        self, X: pd.DataFrame, y: pd.Series
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Discretize the target variable.

        The `fit_resample` method allows for discretizing the target variable.
        The method does not resample the dataset, the naming convention ensure
        the compatibility of the transformer with imbalanced-learn `Pipeline`
        object.

        Args:
            X: Training dataset features
            y: Training dataset target

        Returns:
                Training dataset features and target tuple.
        """

        X, y = check_xy(X, y)

        y = y.apply(self.discretizer)

        return X, y


class CategorySelector(BaseEstimator):
    """Select features and targets rows.

    The `CategorySelector` transformer select features and targets rows
    belonging to given variable categories.

    Parameters:
        variable: variable to be used for selection.
        category: modalities to be selected.
    """

    def __init__(self, variable: str, category: Union[str, list]):

        self.variable = variable
        # Catch or prevent key errors
        if isinstance(category, str):
            self.category = [category]
        elif isinstance(category, list):
            self.category = category
        else:
            raise TypeError(
                f"{self.__class__.__name__} constructor category argument expect a string or a list"
            )

    def fit_resample(
        self, X: pd.DataFrame, y: Optional[pd.Series] = None
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Select features and targets rows.

        The `fit_resample` method allows for selecting the features and target
        rows. The method does not resample the dataset, the naming convention ensure
        the compatibility of the transformer with imbalanced-learn `Pipeline`
        object.

        Args:
            X: Training dataset features
            y: Training dataset target

        Returns:
                Training dataset features and target tuple.
        """

        if isinstance(X, pd.DataFrame) and isinstance(y, pd.Series):
            mask = X[self.variable].isin(self.category)
            XR = X[mask].copy()
            yr = y[mask].copy()

        else:
            raise TypeError(
                f"{self.__class__.__name__} fit_resample methods expect pd.DataFrame and\
                    pd.Series as inputs."
            )

        return XR, yr


class Imputer(SimpleImputer):
    """Impute missing values.

    The `Imputer` transformer wraps scikit-learn SimpleImputer transformer.

    Parameters:
        missing_values: the placeholder for the missing values.
        strategy: the imputation strategy (mean, median, most_frequent, constant).
        fill_value: fill_value is used to replace all occurrences of missing_values (default to 0).
        verbose: controls the verbosity of the imputer.
        copy: If True, a copy of X will be created.
        add_indicator: If True, a MissingIndicator transform will stack onto output of the imputer’s transform.
    """

    def __init__(
        self,
        columns: list,
        missing_values: Union[int, float, str] = np.nan,
        strategy: str = "mean",
        fill_value: float = None,
        verbose: int = 0,
        copy: bool = True,
        add_indicator: bool = False,
    ):
        super().__init__(
            missing_values=missing_values,
            strategy=strategy,
            fill_value=fill_value,
            verbose=verbose,
            copy=copy,
            add_indicator=add_indicator,
        )

        self.columns = columns

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """Fit the imputer on X.

        Args:
            X: Training dataset features.
            y: Training dataset target.

        Returns:
                Transformer.
        """
        X, y = check_xy(X[self.columns], y)

        super().fit(X, y)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Impute X missing values.

        Args:
            X: Training dataset features.

        Returns:
                Transformed training dataset.
        """

        X = check_x(X[self.columns])

        X[X.columns] = super().transform(X)

        return X


class LagTransformer(BaseEstimator, TransformerMixin):
    """Add lags features of the selected columns.

    Lags added correspond to day -1, -3 and -7 and are added to each department separately.

    Parameters:
        date_column: date column.
        zone_columns: geographical zoning column.
        columns: columns to add lag.
    """

    def __init__(self, date_column: str, zone_column: str, columns: List[str]):
        self.date_column = date_column
        self.zone_column = zone_column
        self.columns = columns

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """Fit the imputer on X.

        Args:
            X: Training dataset features.
            y: Training dataset target.

        Returns:
                Transformer.
        """

        X, y = check_xy(X, y)

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Create lag features.

        Args:
            X: Training dataset features.

        Returns:
                Transformed training dataset.
        """

        X = check_x(X)

        if X[self.date_column].dtypes != "datetime64[ns]":
            raise TypeError(
                f"{self.__class__.__name__} transforme methods expect date_column of type datetime64[ns]"
            )

        for var in self.columns:
            for dep in X[self.zone_column].unique():
                tmp = X[X[self.zone_column] == dep][[self.date_column, var]].set_index(
                    self.date_column
                )
                tmp1 = tmp.copy()
                tmp1 = tmp1.join(
                    tmp.shift(periods=1, freq="D"), rsuffix="_lag1", how="left"
                )
                tmp1 = tmp1.join(
                    tmp.shift(periods=3, freq="D"), rsuffix="_lag3", how="left"
                )
                tmp1 = tmp1.join(
                    tmp.shift(periods=7, freq="D"), rsuffix="_lag7", how="left"
                )
                new_vars = [var + "_lag1", var + "_lag3", var + "_lag7"]
                X.loc[X[self.zone_column] == dep, new_vars] = tmp1[new_vars].values
        return X


class FeatureSelector(BaseEstimator, TransformerMixin):
    """Select features correlated to the target.

    Select features with correlation to the target above the threshold.

    Parameters:
        exclude: column to exclude from correlation calculation.
        method: correlation matrix calculation method.
        threshold: columns on which to add lags
    """

    def __init__(
        self, exclude: List[str], method: str = "pearson", threshold: int = 0.15
    ):

        self.exclude = exclude
        self.method = method
        self.threshold = threshold

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """Fit the FeatureSelector on X.

        Compute the correlation matrix.

        Args:
            X: Training dataset features.
            y: Training dataset target.

        Returns:
                Transformer.
        """
        X, y = check_xy(X, y)
        self.target_correlation = (
            pd.concat([X, y], axis=1)
            .corr(method=self.method)
            .loc[y.name]
            .apply(abs)
            .sort_values(ascending=False)
        )
        self.target_correlation = self.target_correlation[
            self.target_correlation.index != y.name
        ]

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Select lag features.

        Args:
            X: Training dataset features.

        Returns:
                Transformed training dataset.
        """

        X = check_x(X)

        mask = self.target_correlation > self.threshold
        self.selected_features = self.target_correlation[mask].index.tolist()

        return X[self.selected_features]


class FeatureSubsetter(BaseEstimator, TransformerMixin):
    """Subset dataframe's column.

    Subset any given of the dataframe.

    Parameters:
        threshold: columns on which to add lags
    """

    def __init__(self, columns: List[str]):

        self.columns = columns

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """Comply with pipeline requirements.

        The method does not fit the dataset, the naming convention ensure
        the compatibility of the transformer with scikit-learn `Pipeline`
        object.

        Args:
            X: Training dataset features.
            y: Training dataset target.

        Returns:
                Transformer.
        """
        X, y = check_xy(X, y)

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Select columns.

        Args:
            X: Training dataset features.

        Returns:
                Training dataset features subset.
        """

        X = check_x(X)

        return X[self.columns]
