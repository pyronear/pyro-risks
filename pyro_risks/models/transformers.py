# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from imblearn.over_sampling import SMOTE
from typing import List, Union, Optional, Tuple, Callable
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import _safe_indexing

from .utils import check_xy, check_x, lagged_dataframe

import pandas as pd
import numpy as np
from scipy import sparse


class TargetDiscretizer(BaseEstimator):

    """Discretize numerical target variable.

    The `TargetDiscretizer` transformer maps target variable values to discrete values using
    a user defined function.

    Parameters:
        discretizer: user defined function.
    """

    def __init__(self, discretizer: Callable) -> None:

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

    def __init__(self, variable: str, category: Union[str, list]) -> None:

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
    ) -> None:
        super().__init__(
            missing_values=missing_values,
            strategy=strategy,
            fill_value=fill_value,
            verbose=verbose,
            copy=copy,
            add_indicator=add_indicator,
        )

        self.columns = columns

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> "Imputer":
        """
        Fit the imputer on X.

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
        """
        Impute X missing values.

        Args:
            X: Training dataset features.

        Returns:
                Transformed training dataset.
        """
        X = check_x(X)
        XS = check_x(X[self.columns])

        X[self.columns] = super().transform(XS)

        return X


class LagTransformer(BaseEstimator, TransformerMixin):

    """Add lags features of the selected columns.

    Lags added correspond to day -1, -3 and -7 and are added to each department separately.

    Parameters:
        date_column: date column.
        zone_columns: geographical zoning column.
        columns: columns to add lag.
        resampling: name of the resampling technique being used.
    """

    def __init__(
        self,
        date_column: str,
        zone_column: str,
        columns: List[str],
        resampling: Optional[str] = "",
    ) -> None:
        self.date_column = date_column
        self.zone_column = zone_column
        self.columns = columns
        self.resampling = resampling

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> "LagTransformer":
        """
        Fit the imputer on X.

        Args:
            X: Training dataset features.
            y: Training dataset target.

        Returns:
                Transformer.
        """
        X, y = check_xy(X, y)

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Create lag features.

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

        if self.resampling == "SMOTE":
            for var in self.columns:
                for dep in X[self.zone_column].unique():
                    # Process original data
                    tmp = X[
                        (X[self.zone_column] == dep) & (X["is_original_data"] == 1)
                    ][[self.date_column, var]].set_index(self.date_column)
                    tmp1 = lagged_dataframe(tmp)
                    new_vars = [var + "_lag1", var + "_lag3", var + "_lag7"]
                    X.loc[
                        (X[self.zone_column] == dep) & (X["is_original_data"] == 1),
                        new_vars,
                    ] = tmp1[new_vars].values

                    # Process SMOTE data
                    tmp = X[
                        (X[self.zone_column] == dep) & (X["is_original_data"] == 0)
                    ][[self.date_column, var]].set_index(self.date_column)
                    tmp1 = lagged_dataframe(tmp)
                    new_vars = [var + "_lag1", var + "_lag3", var + "_lag7"]
                    X.loc[
                        (X[self.zone_column] == dep) & (X["is_original_data"] == 0),
                        new_vars,
                    ] = tmp1[new_vars].values

            return X
        else:
            for var in self.columns:
                for dep in X[self.zone_column].unique():
                    tmp = X[X[self.zone_column] == dep][
                        [self.date_column, var]
                    ].set_index(self.date_column)
                    tmp1 = lagged_dataframe(tmp)
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
        self, exclude: List[str], method: str = "pearson", threshold: float = 0.15
    ) -> None:

        self.exclude = exclude
        self.method = method
        self.threshold = threshold

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> "FeatureSelector":
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
        """
        Select lag features.

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

    def __init__(self, columns: List[str]) -> None:

        self.columns = columns

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> "FeatureSubsetter":
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
        """
        Select columns.

        Args:
            X: Training dataset features.

        Returns:
                Training dataset features subset.
        """
        X = check_x(X)

        return X[self.columns]


class CastTypesToNumeric(BaseEstimator, TransformerMixin):
    def __init__(self, label_encoder: LabelEncoder):
        self.label_encoder = label_encoder

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
        """
        Convert types. SMOTE does not work with category data types and
        datetime objects. Therefore, we encode departement names, and
        convert datetime to timestamps.

        Args:
            X: Original training dataset.

        Returns:
                Training dataset with numeric types.
        """
        X = check_x(X)
        X["day"] = pd.to_numeric(X["day"])
        X["departement"] = X["departement"].astype("category")
        X["departement"] = self.label_encoder.fit_transform(X["departement"])
        return X


class ResetIndex(BaseEstimator):

    """Reset DataFrame and Series indexes.

    The `ResetIndex` transformer resets the indexes of the DataFrame
    and Series.
    It makes some transformations easier (like when replacing values
    in "is_original_data" when generating SMOTE values).
    """

    def fit_resample(
        self, X: pd.DataFrame, y: pd.Series
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Reset DataFrames and Series indexes.

        Args:
            X (pd.DataFrame): Training dataset
            y (pd.Series): Training dataset target

        Returns:
            X (pd.DataFrame): Training dataset with new indexes
            y (pd.Series): Training dataset target with new indexes
        """
        X, y = check_xy(X, y)
        X = X.reset_index(drop=True)
        y = y.reset_index(drop=True)
        return X, y


class CustomSMOTE(SMOTE):

    """Class to perform over-sampling using custom SMOTE.

    The `CustomSMOTE` transformer resamples the dataset using the SMOTE algorithm
    with custom default parameters and additional steps.

    Parameters:
        sampling_strategy (str): specify the class targeted by the resampling. The
          number of samples in the different classes will be equalized. Here
          by default ``'not majority'``, which means it resamples all classes
          but the majority class
        random_state (int): RandomState instance or None
        columns (list of str): DataFrame columns.
    """

    def __init__(
        self,
        *,
        sampling_strategy: str = "not majority",
        random_state: int = None,
        columns: List[str],
    ):
        self.columns = columns
        super().__init__(sampling_strategy=sampling_strategy, random_state=random_state)

    def _fit_resample(
        self, X: pd.DataFrame, y: pd.Series
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Resample the dataset using SMOTE - Synthetic Minority Over-sampling
        Technique.

        Args:
            X (pd.DataFrame): Training dataset
            y (pd.Series): Training dataset target

        Returns:
            X (pd.DataFrame): Training dataset with new rows
            y (pd.Series): Training dataset target with new rows
        """
        self._validate_estimator()

        X_resampled = [X.copy()]
        y_resampled = [y.copy()]

        for class_sample, n_samples in self.sampling_strategy_.items():
            if n_samples == 0:
                continue
            target_class_indices = np.flatnonzero(y == class_sample)
            X_class = _safe_indexing(X, target_class_indices)

            self.nn_k_.fit(X_class)
            nns = self.nn_k_.kneighbors(X_class, return_distance=False)[:, 1:]
            X_new, y_new = self._make_samples(
                X_class, y.dtype, class_sample, X_class, nns, n_samples, 1.0
            )
            X_resampled.append(X_new)
            y_resampled.append(y_new)

        if sparse.issparse(X):
            X_resampled = sparse.vstack(X_resampled, format=X.format)
        else:
            X_resampled = np.vstack(X_resampled)
        y_resampled = np.hstack(y_resampled)

        X = pd.DataFrame(data=X, columns=self.columns)

        X_resampled_df = pd.DataFrame(data=X_resampled, columns=self.columns)
        X_resampled_df["is_original_data"] = 0
        X_resampled_df = X_resampled_df.iloc[len(X) :]  # noqa: E203
        X_resampled_df["day_drop_dup"] = pd.to_datetime(X_resampled_df["day"]).dt.date
        X_resampled_df.drop_duplicates(
            subset=["departement", "day_drop_dup"], inplace=True
        )
        X_resampled_df.drop(columns=["day_drop_dup"], inplace=True)

        X_smote = pd.concat([X, X_resampled_df], axis=0)

        y_resampled_series = pd.Series(y_resampled)
        y_smote = y_resampled_series[y_resampled_series.index.isin(X_smote.index)]
        return X_smote, y_smote


class DecodeLabelsAndTimestamps(BaseEstimator, TransformerMixin):

    """Class to decode previously encoded variables.

    The `DecodeLabelsAndTimestamps` transforms timestamps in dates, and numbers
    in labels.

    Parameters:
        label_encoder (LabelEncoder): the label encoder that was used to encode
        departements.
    """

    def __init__(self, label_encoder: LabelEncoder):
        self.label_encoder = label_encoder

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
        """
        Decoded previously casted/encoded types, to recover the original data
        and proceed to our ML pipeline.

        Args:
            X: Encoded training dataset with SMOTE values.

        Returns:
            X: Decoded training dataset.
        """
        X = check_x(X)

        X_smote_original_dpt = self.label_encoder.inverse_transform(
            np.array(X["departement"])
        )
        X["departement"] = X_smote_original_dpt
        X["day"] = pd.to_datetime(X["day"]).values.astype("datetime64[D]")

        return X
