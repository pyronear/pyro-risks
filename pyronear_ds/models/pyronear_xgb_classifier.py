from typing import Dict, Tuple

import numpy
from pandas import DataFrame, Series
from sklearn.model_selection import (
    BaseCrossValidator,
    cross_val_score,
    cross_val_predict,
)
from xgboost import XGBClassifier


class PyronearXGBoostClassifier(XGBClassifier):
    """
    XGBoost Classifier for fire classification using weather data.
    """

    def __init__(
            self,
            params: Dict[str, str or int],
            label_column: str,
            cross_validator: BaseCrossValidator,
            scoring: str,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.params = params
        self.label_column = label_column
        self.cross_validator = cross_validator
        self.scoring = scoring

    def get_x_y_data(
            self, data: DataFrame, fraction: float = 1
    ) -> Tuple[DataFrame, Series]:
        # randomly shuffle rows and return a fraction of it
        # here the fraction is equal to 1 which means that all rows are returned
        data = data.sample(frac=fraction)
        X = data.drop(self.label_column, axis=1)
        y = data[self.label_column]
        return X, y

    def _get_model(self):
        return XGBClassifier(**self.params)

    def _fit_classifier(
            self, data: DataFrame
    ) -> Tuple[DataFrame, Series, XGBClassifier, numpy.array]:
        X, y = self.get_x_y_data(data)
        model = self._get_model()
        scores = cross_val_score(
            model, X, y, cv=self.cross_validator, scoring=self.scoring, n_jobs=-1
        )
        return X, y, model, scores

    def get_predictions_and_scores(
            self, data: DataFrame
    ) -> Tuple[numpy.array, numpy.ndarray]:
        X, y, model, scores = self._fit_classifier(data)
        predictions = cross_val_predict(model, X, y, cv=self.cross_validator, n_jobs=-1)
        return scores, predictions
