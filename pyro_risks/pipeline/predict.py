# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

# type: ignore
from pyro_risks import config as cfg
from pyro_risks.datasets.fwi import get_fwi_data_for_predict
from pyro_risks.datasets.ERA5 import get_data_era5t_for_predict
from pyro_risks.datasets.era_fwi_viirs import process_dataset_to_predict
from typing import Optional, List
from io import BytesIO

import pandas as pd
import dvc.api
import joblib
import logging
import os


__all__ = ["PyroRisk"]


class PyroRisk(object):
    """
    Pyronear Wildfire Risk Forecaster

    Load a trained pipeline from pyrorisks remote model registry, download features from publicly
    available data sources (CDS API). Forecast the local (NUTS 3 level) daily wildfire risks
    (forest fire danger) in a Given Country (France).

    Args:
        model: Can be 'RF' for random forest or 'XGBOOST' for xgboost. Defaults to 'RF'.

    Raises:
        ValueError: Model can be only of type RF or XGBOOST
    """

    def __init__(self, model: Optional[str] = "RF") -> None:
        self.inputs = None
        self.model = model
        self.pipeline = None
        self.predictions = None
        self.country = None
        self.zone = None
        self.predictions_registry = cfg.PREDICTIONS_REGISTRY

        if self.model == "RF":
            self.model_path = cfg.RFMODEL_ERA5T_PATH  # file path
        elif self.model == "XGBOOST":
            self.model_path = cfg.XGBMODEL_ERA5T_PATH  # file path
        else:
            raise ValueError("Model can be only of type RF or XGBOOST")

    def get_pipeline(
        self, path: Optional[str] = None, destination: Optional[str] = None
    ) -> None:
        """Download trained pipeline from remote model registry.

        The `get_pipeline` method downloads the selected trained pipeline from the pyrorisks remote
        model registry. The downloaded pipeline is persited in the destination joblib file.

        Args:
            path: Location and file name of the pipeline to download, relative to the root of the
            dvc project. Defaults to None (self.model_path).
            destination: Location where the pipeline is downloaded. Defaults to None (self.model_path).
        """
        path = self.model_path if path is None else path
        destination = self.model_path if destination is None else destination

        pipeline = joblib.load(
            BytesIO(
                dvc.api.read(
                    path=path, repo=cfg.REPO_DIR, remote="artifacts-registry", mode="rb"
                )
            )
        )
        joblib.dump(pipeline, destination)

    @staticmethod
    def get_inputs(
        day: str,
        country: Optional[str] = "France",
        dir_destination: Optional[str] = None,
    ) -> None:
        """Download datasets and build features for forecasting daily wildfire risks on a given date.

        The `get_inputs` method downloads datsets from publicly available data sources (CDS API) and
        build features for forecasting wildfire risks on a given date. The downloaded inputs are
        persited in the destination csv file.

        Args:
            day: Date of interest ('%Y-%m-%d') for example '2020-05-05'.
            country: Country of interest. Defaults to 'France'.
            destination: Location where the daily inputs are persisted.
            Defaults to None (cfg.PIPELINE_INPUT_PATH).
        """
        # TODO:
        # Delete get_fwi_data_for_predict variables not available at predict time
        # Create process_era5 function
        # Create MergedEraViir class
        dir_destination = (
            cfg.PREDICTIONS_REGISTRY if dir_destination is None else dir_destination
        )
        fname = f"inputs_{country}_{day}.csv"
        destination = os.path.join(dir_destination, fname)
        fwi = get_fwi_data_for_predict(day)
        era = get_data_era5t_for_predict(day)
        res_test = process_dataset_to_predict(fwi, era)
        res_test = res_test.rename({"nom": "departement"}, axis=1)
        res_test.to_csv(destination)

    def load_pipeline(self, path: Optional[str] = None) -> None:
        """Load trained pipeline from local path.

        Args:
            path: Location where the pipeline has been downloaded. Defaults to None (self.model_path).
        """
        path = self.model_path if path is None else path

        if os.path.isfile(path):
            self.pipeline = joblib.load(path)
        else:
            self.get_pipeline(destination=path)
            self.pipeline = joblib.load(path)

    def load_inputs(
        self,
        day: str,
        country: Optional[str] = "France",
        usecols: Optional[List[str]] = None,
        dir_path: Optional[str] = None,
    ) -> None:
        """Load inputs from local path.

        Args:
            day: Date of interest ('%Y-%m-%d') for example '2020-05-05'.
            country: Country of interest. Defaults to 'France'.
            dir_path: Location where the daily inputs have been persisted. Defaults to None
            (cfg.PREDICTIONS_REGISTRY).
        """
        dir_path = cfg.PREDICTIONS_REGISTRY if dir_path is None else dir_path
        usecols = cfg.PIPELINE_COLS if usecols is None else usecols
        fname = f"inputs_{country}_{day}.csv"

        path = os.path.join(dir_path, fname)

        if os.path.isfile(path):
            self.inputs = pd.read_csv(path, usecols=usecols)
        else:
            self.get_inputs(day=day, country=country, dir_destination=dir_path)
            self.inputs = pd.read_csv(path, usecols=usecols)
        self.inputs[cfg.DATE_VAR] = pd.to_datetime(self.inputs[cfg.DATE_VAR])

    def predict(
        self,
        day: str,
        country: Optional[str] = "France",
        zone_column: Optional[str] = cfg.ZONE_VAR,
        dir_destination: Optional[str] = None,
    ) -> None:
        """Predict local daily wildfire risks in a given country.

        Forecast the local (NUTS 3 level) daily wildfire risks (forest fire danger) in a given
        country (France). Note that predictions on fwi and era5land data queried from CDS API
        will return 93 departments instead of 96 for France.

        Args:
            day: Date of interest ('%Y-%m-%d') for example '2020-05-05'.
            country: Country of interest. Defaults to 'France'.
            dir_destination: Location where the daily inputs are persisted.
            Defaults to None (cfg.PREDICTIONS_REGISTRY).
        """
        path = (
            os.path.join(dir_destination, f"{self.model}.joblib")
            if dir_destination is not None
            else os.path.join(cfg.PREDICTIONS_REGISTRY, f"{self.model}.joblib")
        )
        self.load_pipeline(path=path)
        self.load_inputs(day=day, country=country, dir_path=dir_destination)

        fname = f"{self.model}_predictions_{country}_{day}.joblib"
        destination = os.path.join(dir_destination, fname)

        if self.model == "RF":
            self.predictions = self.pipeline.predict_proba(self.inputs)
            res = dict(zip(self.inputs[zone_column], self.predictions[:, 1].round(3)))
        elif self.model == "XGBOOST":
            self.predictions = self.pipeline.predict_proba(self.inputs)
            res = dict(zip(self.inputs[zone_column], self.predictions.round(3)))
        logging.info(
            f"Predict {country} local wildfire risks on {day}, using {self.model} pipeline."
        )
        joblib.dump(res, destination)

    def get_predictions(
        self,
        day: str,
        country: Optional[str] = "France",
        dir_path: Optional[str] = None,
        dir_destination: Optional[str] = None,
    ) -> None:
        """Download predictions for the day of interest from the remote prediction registry.

        The `get_predictions` method downloads the forecasted local wildfire risks at a given
        day in a given country (France). The downloaded predictions are persited in the
        destination joblib file.

        Args:
            day: Date of interest ('%Y-%m-%d') for example '2020-05-05'.
            country: Country of interest. Defaults to 'France'.
            dir_path: Location of the predictions to download, relative to the root of the dvc project.
            Defaults to None.
            dir_destination: Location where the daily predictions are persisted. Defaults to None.
        """
        dir_path = cfg.PREDICTIONS_REGISTRY if dir_path is None else dir_path
        dir_destination = (
            cfg.PREDICTIONS_REGISTRY if dir_destination is None else dir_destination
        )
        fname = f"{self.model}_predictions_{country}_{day}.joblib"
        destination = os.path.join(dir_destination, fname)
        path = os.path.join(dir_path, fname)

        predictions = joblib.load(
            BytesIO(
                dvc.api.read(
                    path=path, repo=cfg.REPO_DIR, remote="artifacts-registry", mode="rb"
                )
            )
        )
        joblib.dump(predictions, destination)

    def expose_predictions(
        self,
        day: str,
        country: Optional[str] = "France",
        dir_path: Optional[str] = None,
        dir_destination: Optional[str] = None,
    ) -> dict:
        """Serves a prediction for the specified day.

        Args:
            day: Date of interest ('%Y-%m-%d') for example '2020-05-05'.
            country: Country of interest. Defaults to 'France'.
            dir_path: Location of the predictions to download, relative to the root of the dvc project.
            Defaults to None.

        Returns:
            dict[dict]: keys are departements, values dictionaries whose keys are score and explainability
            and values probability predictions for label 1 (fire) and feature contributions to predictions
            respectively.
        """
        fname = f"{self.model}_predictions_{country}_{day}.joblib"
        path = os.path.join(dir_destination, fname)

        if os.path.isfile(path):
            self.predictions = joblib.load(path)
        else:
            self.get_predictions(
                day=day,
                country=country,
                dir_path=dir_path,
                dir_destination=dir_destination,
            )
            self.predictions = joblib.load(path)
        return {
            x: {"score": self.predictions[x], "explainability": None}
            for x in self.predictions
        }
