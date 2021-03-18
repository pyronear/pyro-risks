# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from pyro_risks.main import _download, _train_pipeline, _evaluate_pipeline
from click.testing import CliRunner

import unittest

class MainTester(unittest.TestCase):

    def test_dowload(self):

    def test_train_pipeline(self):
        Args = namedtuple(
            "args", ["model", "destination", "ignore_prints", "ignore_html"]
        )
        pattern = "/*.joblib"
        with tempfile.TemporaryDirectory() as destination:
            args = Args("RF", destination, True, True)
            _train_pipeline(args)
            files = glob.glob(destination + pattern)
            self.assertTrue(any(["RF" in file for file in files]))

    def test_evaluate_pipeline(self):
        usecols = [cfg.DATE_VAR, cfg.ZONE_VAR, cfg.TARGET] + cfg.PIPELINE_ERA5T_VARS
        pipeline_vars = [cfg.DATE_VAR, cfg.ZONE_VAR] + cfg.PIPELINE_ERA5T_VARS
        df = pd.read_csv(cfg.ERA5T_VIIRS_PIPELINE, usecols=usecols)
        df["day"] = df["day"].apply(
            lambda x: datetime.strptime(str(x), "%Y-%m-%d") if not pd.isnull(x) else x
        )
        X = df[pipeline_vars]
        y = df[cfg.TARGET]

        dummy_pipeline = Pipeline(
            [("dummy_classifier", DummyClassifier(strategy="constant", constant=0))]
        )

        Args = namedtuple("args", ["pipeline", "threshold", "prefix", "destination"])

        with tempfile.TemporaryDirectory() as destination:
            train_pipeline(
                X=X,
                y=y,
                model="DUMMY",
                pipeline=dummy_pipeline,
                destination=destination,
                ignore_prints=True,
                ignore_html=True,
            )
            pipeline_path = glob.glob(destination + "/*.joblib")
            args = Args(pipeline_path[0], 0, "DUMMY", destination)
            main(args)
            files = glob.glob(destination + "/*")
            self.assertTrue(any([".png" in file for file in files]))
            self.assertTrue(any([".json" in file for file in files]))
            self.assertTrue(any([".csv" in file for file in files]))




if __name__ =="__main__":
    unittest.main()