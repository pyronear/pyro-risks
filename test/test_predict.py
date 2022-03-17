# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from pyro_risks.pipeline import PyroRisk
from pyro_risks import config as cfg

import pandas as pd

import requests
import imblearn
import unittest
import tempfile
import glob
import os


class PredictTester(unittest.TestCase):
    def test_pyrorisk(self):
        pyrorisk_rf = PyroRisk()
        pyrorisk_xgb = PyroRisk(model="XGBOOST")
        self.assertEqual(pyrorisk_rf.model, "RF")
        self.assertEqual(pyrorisk_xgb.model, "XGBOOST")
        self.assertEqual(pyrorisk_rf.model_path, cfg.RFMODEL_ERA5T_PATH)
        self.assertEqual(pyrorisk_xgb.model_path, cfg.XGBMODEL_ERA5T_PATH)
        self.assertEqual(pyrorisk_rf.predictions_registry, cfg.PREDICTIONS_REGISTRY)
        self.assertEqual(pyrorisk_xgb.predictions_registry, cfg.PREDICTIONS_REGISTRY)
        with self.assertRaises(ValueError):
            PyroRisk(model="`Mock`")

    def test_get_pipeline(self):
        pyrorisk = PyroRisk()
        with tempfile.TemporaryDirectory() as dir_destination:
            destination = f"{dir_destination}/RF.joblib"
            pyrorisk.get_pipeline(destination=destination)
            files = glob.glob(dir_destination + "/*")
            self.assertTrue(any(["RF.joblib" in file for file in files]))

    def test_get_inputs(self):
        pyrorisk = PyroRisk()
        country = "France"
        day = "2020-05-05"
        with tempfile.TemporaryDirectory() as dir_destination:
            pyrorisk.get_inputs(
                day=day, country=country, dir_destination=dir_destination
            )
            files = glob.glob(dir_destination + "/*")
            self.assertTrue(
                any([f"inputs_{country}_{day}.csv" in file for file in files])
            )

    def test_load_pipeline(self):
        pyrorisk = PyroRisk()
        with tempfile.TemporaryDirectory() as dir_path:
            path = dir_path + "/RF.joblib"
            pyrorisk.load_pipeline(path=path)
            files = glob.glob(dir_path + "/*")
            self.assertTrue(isinstance(pyrorisk.pipeline, imblearn.pipeline.Pipeline))
            self.assertTrue(any(["RF.joblib" in file for file in files]))
            pyrorisk.pipeline = None
            pyrorisk.load_pipeline(path=path)
            self.assertTrue(isinstance(pyrorisk.pipeline, imblearn.pipeline.Pipeline))

    def test_load_inputs(self):
        pyrorisk = PyroRisk()
        country = "France"
        day = "2020-05-05"
        with tempfile.TemporaryDirectory() as dir_path:
            pyrorisk.load_inputs(day=day, country=country, dir_path=dir_path)
            files = glob.glob(dir_path + "/*")
            self.assertTrue(isinstance(pyrorisk.inputs, pd.DataFrame))
            self.assertTrue(
                any([f"inputs_{country}_{day}.csv" in file for file in files])
            )
            pyrorisk.inputs = None
            pyrorisk.load_inputs(day=day, country=country, dir_path=dir_path)
            self.assertTrue(isinstance(pyrorisk.inputs, pd.DataFrame))

    def test_predict(self):
        pyrorisk_rf = PyroRisk()
        pyrorisk_xgb = PyroRisk(model="XGBOOST")
        country = "France"
        day = "2020-05-05"
        inputs_fname = "inputs_France_2020-05-05.csv"
        rf_pipeline_fname = "RF.joblib"
        xgb_pipeline_fname = "XGBOOST.joblib"
        mock_inputs = requests.get(
            url="https://github.com/pyronear/pyro-risks/releases/download/v0.1.0-data/inputs_France_2020-05-05.csv"
        )
        mock_rf_pipeline = requests.get(
            url="https://github.com/pyronear/pyro-risks/releases/download/v0.1.0-data/RF.joblib"
        )
        mock_xgb_pipeline = requests.get(
            url="https://github.com/pyronear/pyro-risks/releases/download/v0.1.0-data/RF.joblib"
        )

        with tempfile.TemporaryDirectory() as dir_destination:
            with open(os.path.join(dir_destination, inputs_fname), "wb") as inputs:
                inputs.write(mock_inputs.content)

            with open(
                os.path.join(dir_destination, rf_pipeline_fname), "wb"
            ) as pipeline:
                pipeline.write(mock_rf_pipeline.content)
            with open(
                os.path.join(dir_destination, xgb_pipeline_fname), "wb"
            ) as pipeline:
                pipeline.write(mock_xgb_pipeline.content)
            pyrorisk_rf.predict(
                day=day, country=country, dir_destination=dir_destination
            )
            pyrorisk_xgb.predict(
                day=day, country=country, dir_destination=dir_destination
            )
            files = glob.glob(dir_destination + "/*")
            self.assertTrue(
                any(
                    [
                        f"{pyrorisk_rf.model}_predictions_{country}_{day}.joblib"
                        in file
                        for file in files
                    ]
                )
            )
            self.assertTrue(
                any(
                    [
                        f"{pyrorisk_xgb.model}_predictions_{country}_{day}.joblib"
                        in file
                        for file in files
                    ]
                )
            )

    def test_get_predictions(self):
        pyrorisk = PyroRisk()
        country = "France"
        day = "2020-05-05"
        with tempfile.TemporaryDirectory() as destination:
            pyrorisk.get_predictions(day=day, dir_destination=destination)
            files = glob.glob(destination + "/*")
            self.assertTrue(
                any(
                    [
                        f"{pyrorisk.model}_predictions_{country}_{day}.joblib" in file
                        for file in files
                    ]
                )
            )

    def test_expose_predictions(self):
        pyrorisk = PyroRisk()
        day = "2020-05-05"
        with tempfile.TemporaryDirectory() as destination:
            predictions_dict = pyrorisk.expose_predictions(
                day=day, dir_destination=destination
            )
            predictions_load_dict = pyrorisk.expose_predictions(
                day=day, dir_destination=destination
            )

        self.assertTrue(isinstance(predictions_dict, dict))
        self.assertTrue(isinstance(predictions_load_dict, dict))


if __name__ == "__main__":
    unittest.main()
