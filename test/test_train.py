# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

import unittest
from unittest.mock import patch
import tempfile
import glob
import os

import numpy as np
import pandas as pd
from pyro_risks.models import xgb_pipeline, rf_pipeline
from pyro_risks.train import calibrate_pipeline, save_pipeline


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
        pattern = "/*.joblib"

        with tempfile.TemporaryDirectory() as destination:
            save_pipeline(
                pipeline=xgb_pipeline,
                model="XGBOOST",
                optimal_threshold=optimal_threshold,
                destination=destination,
                ignore_html=True,
            )
            save_pipeline(
                pipeline=rf_pipeline,
                model="RF",
                optimal_threshold=optimal_threshold,
                destination=destination,
                ignore_html=True,
            )
            files = glob.glob(destination + pattern)
            self.assertTrue(any(["RF_0-35" in file for file in files]))
            self.assertTrue(any(["XGBOOST_0-35" in file for file in files]))


if __name__ == "__main__":
    unittest.main()
