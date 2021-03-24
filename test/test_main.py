# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from pyro_risks.main import main, _download, _train_pipeline, _evaluate_pipeline
from pyro_risks.pipeline import load_dataset
from pyro_risks.pipeline import train_pipeline
from imblearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from click.testing import CliRunner


import pyro_risks.config as cfg

import unittest
import tempfile
import glob
import os


class MainTester(unittest.TestCase):
    def test_download(self):
        runner = CliRunner()
        pattern = "/*.csv"
        with tempfile.TemporaryDirectory() as destination:
            runner.invoke(main, ["download", "--destination", destination])
            files = glob.glob(destination + pattern)
            self.assertTrue(any([cfg.DATASET in file for file in files]))

    def test_train_pipeline(self):
        runner = CliRunner()
        pattern = "/*.joblib"
        with tempfile.TemporaryDirectory() as destination:
            runner.invoke(
                main, ["train", "--model", "RF", "--destination", destination]
            )
            files = glob.glob(destination + pattern)
            self.assertTrue(any(["RF" in file for file in files]))

    def test_evaluate_pipeline(self):
        runner = CliRunner()
        pattern = "/*.joblib"
        X, y = load_dataset()

        dummy_pipeline = Pipeline(
            [("dummy_classifier", DummyClassifier(strategy="constant", constant=0))]
        )

        with tempfile.TemporaryDirectory() as destination:
            threshold = destination + "/DUMMY_threshold.json"
            train_pipeline(
                X=X,
                y=y,
                model="DUMMY",
                pipeline=dummy_pipeline,
                destination=destination,
                ignore_prints=True,
                ignore_html=True,
            )
            pipeline_path = glob.glob(destination + pattern)
            runner.invoke(
                main,
                [
                    "evaluate",
                    "--pipeline",
                    pipeline_path[0],
                    "--threshold",
                    threshold,
                    "--prefix",
                    "DUMMY",
                    "--destination",
                    destination,
                ],
            )
            files = glob.glob(destination + "/*")
            self.assertTrue(any([".png" in file for file in files]))
            self.assertTrue(any([".json" in file for file in files]))
            self.assertTrue(any([".csv" in file for file in files]))


if __name__ == "__main__":
    unittest.main()
