# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import unittest
from collections import namedtuple
import tempfile
import glob


import numpy as np
import pandas as pd
import pyro_risks.config as cfg

from datetime import datetime
from imblearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from pyro_risks.models import xgb_pipeline, rf_pipeline
from pyro_risks.pipeline import (
    calibrate_pipeline,
    save_pipeline,
    train_pipeline,
    load_dataset,
)


class TrainTester(unittest.TestCase):
    def test_calibrate_pipeline(self):
        y_true = np.array([0, 0, 1, 1])
        y_scores = np.array([[0.9, 0.1], [0.6, 0.4], [0.65, 0.35], [0.2, 0.8]])
        optimal_threshold = calibrate_pipeline(y_true, y_scores)
        self.assertEqual(optimal_threshold, 0.35)

    def test_save_pipeline(self):
        y_true = np.array([0, 0, 1, 1])
        y_scores = np.array([[0.9, 0.1], [0.6, 0.4], [0.65, 0.35], [0.2, 0.8]])
        optimal_threshold = calibrate_pipeline(y_true, y_scores)
        model_pattern = "/*.joblib"
        html_pattern = "/*.html"
        registry = "/.model_registry"

        with tempfile.TemporaryDirectory() as destination:
            save_pipeline(
                pipeline=xgb_pipeline,
                model="RF",
                optimal_threshold=optimal_threshold,
                destination=destination,
                ignore_html=True,
            )
            save_pipeline(
                pipeline=rf_pipeline,
                model="RF",
                optimal_threshold=optimal_threshold,
                destination=destination,
                ignore_html=False,
            )
            model_files = glob.glob(destination + model_pattern)
            html_files = glob.glob(destination + html_pattern)
            self.assertTrue(any(["RF" in file for file in model_files]))
            self.assertTrue(any(["RF" in file for file in html_files]))

        with tempfile.TemporaryDirectory() as destination:
            save_pipeline(
                pipeline=xgb_pipeline,
                model="XGBOOST",
                optimal_threshold=optimal_threshold,
                destination=destination + registry,
                ignore_html=True,
            )
            save_pipeline(
                pipeline=rf_pipeline,
                model="XGBOOST",
                optimal_threshold=optimal_threshold,
                destination=destination + registry,
                ignore_html=False,
            )
            model_files = glob.glob(destination + registry + model_pattern)
            html_files = glob.glob(destination + registry + html_pattern)
            self.assertTrue(any(["XGBOOST" in file for file in model_files]))
            self.assertTrue(any(["XGBOOST" in file for file in html_files]))

    def test_train_pipeline(self):
        X, y = load_dataset()
        pattern = "/*.joblib"

        dummy_pipeline = Pipeline(
            [("dummy_classifier", DummyClassifier(strategy="constant", constant=0))]
        )
        with tempfile.TemporaryDirectory() as destination:
            train_pipeline(
                X=X,
                y=y,
                model="XGBOOST",
                destination=destination,
                ignore_prints=True,
                ignore_html=True,
            )
            train_pipeline(
                X=X,
                y=y,
                model="RF",
                destination=destination,
                ignore_prints=True,
                ignore_html=True,
            )
            train_pipeline(
                X=X,
                y=y,
                model="DUMMY",
                pipeline=dummy_pipeline,
                destination=destination,
                ignore_prints=True,
                ignore_html=True,
            )
            files = glob.glob(destination + pattern)
            self.assertTrue(any(["RF" in file for file in files]))
            self.assertTrue(any(["XGBOOST" in file for file in files]))
            self.assertTrue(any(["DUMMY" in file for file in files]))


if __name__ == "__main__":
    unittest.main()
