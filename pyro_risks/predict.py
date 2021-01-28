import joblib
from urllib.request import urlopen
import xgboost

from pyro_risks import config as cfg
from pyro_risks.datasets.fwi import get_fwi_data_for_predict
from pyro_risks.datasets.ERA5 import (
    get_data_era5land_for_predict,
    get_data_era5t_for_predict,
)
from pyro_risks.datasets.era_fwi_viirs import process_dataset_to_predict
from .score_v0 import add_lags

__all__ = ["PyroRisk"]


class PyroRisk(object):
    """Pyronear risk score for fire danger on French departments.

    Load a trained model uploaded on the Pyro-risk Github Release to get predictions for a selected day

    Args:
        object ([type])
    """

    def __init__(self, which="RF"):
        """Load from Github release the trained model. For the moment only RF and XGB are available.

        Args:
            which (str, optional): Can be 'RF' for random forest or 'XGB' for xgboost. Defaults to 'RF'.
        """
        if which == "RF":
            self.model_path = cfg.RFMODEL_ERA5T_PATH
        elif which == "XGB":
            self.model_path = cfg.XGBMODEL_ERA5T_PATH
        else:
            raise ValueError("Model can be only of type RF or XGB")
        self.model = joblib.load(urlopen(self.model_path))
        self._model_type = which

    def get_input(self, day):
        """Returns for a given day data to feed into the model.

        This makes use of the CDS API to query data for the selected day, add lags and select
        variables used by the model.

        Args:
            day (str): for example '2020-05-05'

        Returns:
            pd.DataFrame
        """
        model_cols = cfg.MODEL_ERA5T_VARS
        fwi = get_fwi_data_for_predict(day)
        era = get_data_era5t_for_predict(day)
        res_test = process_dataset_to_predict(fwi, era)
        res_test = res_test.rename({"nom": "departement"}, axis=1)
        # Add lags only for columns on which model was trained on
        cols_lags = [
            "_".join(x.split("_")[:-1])
            for x in cfg.MODEL_ERA5T_VARS
            if "_lag" in x
        ]
        res_lags = add_lags(res_test, cols_lags)
        # Select only rows corresponding to day
        to_predict = res_lags.loc[res_lags["day"] == day]
        to_predict = to_predict.drop("day", axis=1).set_index("departement")
        # Some NaN due to the aggregations on departments with only one line (variables with std)
        to_predict = to_predict.fillna(0)
        return to_predict[model_cols]

    def predict(self, day, country="France"):
        """Serves a prediction for the specified day.

        Note that predictions on fwi and era5land data queried from CDS API will return 93 departments
        instead of 96 for France.

        Args:
            day (str): like '2020-05-05'
            country (str, optional): Defaults to 'France'.

        Returns:
            dict: keys are departements, values dictionaries whose keys are score and explainability
            and values probability predictions for label 1 (fire) and feature contributions to predictions
            respectively
        """
        sample = self.get_input(day)
        if self._model_type == "RF":
            predictions = self.model.predict_proba(sample.values)
            res = dict(zip(sample.index, predictions[:, 1].round(3)))
        elif self._model_type == "XGB":
            predictions = self.model.predict(xgboost.DMatrix(sample))
            res = dict(zip(sample.index, predictions.round(3)))
        return {x: {"score": res[x], "explainability": None} for x in res}
