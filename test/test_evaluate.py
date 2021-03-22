# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from collections import namedtuple
from datetime import datetime
from imblearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
from pyro_risks.pipeline import train_pipeline, save_pipeline
from pyro_risks.pipeline import (
    save_classification_reports,
    save_classification_plots,
    evaluate_pipeline,
)


import numpy as np
import pandas as pd
import pyro_risks.config as cfg

import unittest
import tempfile
import glob


class EvaluateTester(unittest.TestCase):
    def test_save_classification_reports(self):
        y_true = np.array([0, 0, 1, 1])
        y_pred = np.array([0, 1, 1, 1])
        with tempfile.TemporaryDirectory() as destination:
            save_classification_reports(
                y_true=y_true, y_pred=y_pred, prefix="TEST", destination=destination
            )
            files = glob.glob(destination + "/*")
            self.assertTrue(any([".json" in file for file in files]))
            self.assertTrue(any([".csv" in file for file in files]))

    def test_save_classification_plots(self):
        y_true = np.array([0, 0, 1, 1])
        y_proba = np.array([[0.9, 0.1], [0.6, 0.4], [0.65, 0.35], [0.2, 0.8]])
        with tempfile.TemporaryDirectory() as destination:
            save_classification_plots(
                y_true=y_true,
                y_proba=y_proba[:, 1],
                threshold=0.35,
                prefix="TEST",
                destination=destination,
            )
            files = glob.glob(destination + "/*")
            self.assertTrue(any([".png" in file for file in files]))

    def test_evaluate_pipeline(self):
        X, y = make_classification(
            n_samples=100, n_features=5, n_informative=2, n_redundant=2
        )
        X_train, _, y_train, _ = train_test_split(
            X, y, test_size=cfg.TEST_SIZE, random_state=cfg.RANDOM_STATE
        )
        dummy_pipeline = Pipeline(
            [("dummy_classifier", DummyClassifier(strategy="constant", constant=0))]
        )
        dummy_pipeline.fit(X_train, y_train)

        with tempfile.TemporaryDirectory() as destination:
            threshold = destination + "/DUMMY_threshold.json"
            save_pipeline(
                pipeline=dummy_pipeline,
                model="DUMMY",
                optimal_threshold=0,
                destination=destination,
            )
            evaluate_pipeline(
                X=X,
                y=y,
                pipeline=dummy_pipeline,
                threshold=threshold,
                prefix="DUMMY",
                destination=destination,
            )
            files = glob.glob(destination + "/*")
            self.assertTrue(any([".png" in file for file in files]))
            self.assertTrue(any([".json" in file for file in files]))
            self.assertTrue(any([".csv" in file for file in files]))


if __name__ == "__main__":
    unittest.main()
