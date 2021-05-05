# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from typing import List, Union, Optional, Tuple

from imblearn.over_sampling import SMOTE
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder

from .utils import check_xy, check_x, lagged_dataframe, discretizer

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

    def __init__(self, date_column: str, zone_column: str, columns: List[str], resampling: Optional[str] = ""):
        self.date_column = date_column
        self.zone_column = zone_column
        self.columns = columns
        self.resampling = resampling

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
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
                    tmp = X[(X[self.zone_column] == dep) & (X["is_original_data"] == 1)][
                        [self.date_column, var]].set_index(
                        self.date_column
                    )
                    tmp1 = lagged_dataframe(tmp)
                    new_vars = [var + "_lag1", var + "_lag3", var + "_lag7"]
                    X.loc[(X[self.zone_column] == dep) & (X["is_original_data"] == 1), new_vars] = tmp1[new_vars].values

                    # Process SMOTE data
                    tmp = X[(X[self.zone_column] == dep) & (X["is_original_data"] == 0)][
                        [self.date_column, var]].set_index(
                        self.date_column
                    )
                    tmp1 = lagged_dataframe(tmp)
                    new_vars = [var + "_lag1", var + "_lag3", var + "_lag7"]
                    X.loc[(X[self.zone_column] == dep) & (X["is_original_data"] == 0), new_vars] = tmp1[new_vars].values

            return X
        else:
            for var in self.columns:
                for dep in X[self.zone_column].unique():
                    tmp = X[X[self.zone_column] == dep][[self.date_column, var]].set_index(
                        self.date_column
                    )
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
        """
        Select columns.

        Args:
            X: Training dataset features.

        Returns:
                Training dataset features subset.
        """
        X = check_x(X)

        return X[self.columns]


class SMOTEDataGenerator(BaseEstimator):

    """Generate more data.

    The `SMOTEDataGenerator` uses the SMOTE oversampling technique to generate more data for our training.

    Parameters:
        random_state: random state for the SMOTE dataset generation.
    """

    def __init__(self, random_state: int):
        self.random_state = random_state

    def fit_resample(
        self, X: pd.DataFrame, y: Optional[pd.Series] = None
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Select features and targets rows.

        The `fit_resample` method allows for producing new data using SMOTE method.
        We have several steps here, maybe they can be implemented in separate methods.
        I just have to look at the imabalanced-learn documentation :
            1. Processing whole dataset for SMOTE
                1. days cannot be Timestamps for SMOTE
                2. departements have to be put in category because SMOTE doesn't work with category data
            2. Handling missing values
            3. Generate SMOTE data
            4. Process SMOTE only generated values
                1. Clean it : delete impossible combination of values that have been generated
                (several rows for the same day same department)
            5. Final SMOTE df generation
            6. Adjust y_smote with correct indices for training
            7. Retroprocessing : undo the category encoding we did earlier

        Args:
            X: Training dataset features
            y: Training dataset target

        Returns:
            X_smote: Training dataset, augmented by SMOTE oversampling technique
            y_smote: Training dataset, augmented by SMOTE oversampling technique
        """
        le = LabelEncoder()
        X["day"] = pd.to_numeric(X["day"])
        X["departement"] = X["departement"].astype("category")
        X = X.reset_index(drop=True)
        y = y.reset_index(drop=True)

        X['departement'] = le.fit_transform(X['departement'])

        imp = Imputer(strategy="median", columns=["asn_std", "rsn_std"])
        imp.fit(X, y)
        X = imp.transform(X)

        sm = SMOTE(sampling_strategy='not majority', random_state=self.random_state)

        vdiscretizer = np.vectorize(discretizer)

        y_vectorized = vdiscretizer(y)
        X_smote_all, y_smote_tmp = sm.fit_resample(X, y_vectorized)
        y_smote_tmp = pd.Series(y_smote_tmp)

        X_smote_tmp = X_smote_all.iloc[len(X):]

        X_smote_tmp["day_drop_dup"] = pd.to_datetime(X_smote_tmp["day"]).dt.date
        X_smote_tmp = X_smote_tmp.drop_duplicates(subset=["departement", "day_drop_dup"])
        X_smote_tmp.drop(columns=["day_drop_dup"], inplace=True)

        X["is_original_data"] = 1
        X_smote = pd.concat([X, X_smote_tmp], axis=0).fillna(0)

        y_smote = y_smote_tmp[y_smote_tmp.index.isin(X_smote.index)]
        X_smote = X_smote.reset_index(drop=True)
        y_smote = y_smote.reset_index(drop=True)

        X_smote_original_dpt = le.inverse_transform(np.array(X_smote["departement"]))
        X_smote["departement"] = X_smote_original_dpt
        X_smote["day"] = pd.to_datetime(X_smote["day"]).values.astype('datetime64[D]')

        return X_smote, y_smote

