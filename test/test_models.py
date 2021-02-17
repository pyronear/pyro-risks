import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal
from sklearn.datasets import load_breast_cancer

from pyro_risks import score_v0, predict
from pyro_risks import config as cfg


class ModelsTester(unittest.TestCase):

    def test_prepare_dataset(self):
        df = pd.DataFrame({
            "day": ["2019-07-01", "2019-08-02", "2019-06-12"],
            "departement": ["Aisne", "Cantal", "Savoie"],
            "fires": [0, 5, 10],
            "fwi_mean": [13.3, 0.9, 2.5],
            "ffmc_max": [23, 45.3, 109.0],
        })
        X, y = score_v0.prepare_dataset(df, selected_dep=["Aisne", "Cantal"])
        assert_frame_equal(
            X,
            pd.DataFrame({
                "fwi_mean": {
                    0: 13.3,
                    1: 0.9
                },
                "ffmc_max": {
                    0: 23.0,
                    1: 45.3
                }
            }),
        )
        assert_series_equal(y, pd.Series([0, 1], name="classif_target"))

    def test_target_correlated_features(self):
        X = pd.DataFrame({
            "str_mean": [2, 3, 4, 0, 0],
            "ffmc_min": [0, 0, 0, 0, 0],
            "isi_mean": [3, 0, 1, 4, 5],
        })
        y = pd.Series(np.array([1, 1, 1, 0, 0]), name="classif_target")
        self.assertEqual(score_v0.target_correlated_features(X, y),
                         ["str_mean", "isi_mean"])

    def test_add_lags(self):
        df = pd.DataFrame({
            "day": ["2019-07-01", "2019-07-04", "2019-07-07", "2019-07-08"],
            "departement": ["Cantal", "Cantal", "Cantal", "Cantal"],
            "fwi_mean": [1.1, 13.3, 0.9, 2.5],
        })
        df["day"] = pd.to_datetime(df["day"])
        res = pd.DataFrame({
            "day": {
                0: np.datetime64("2019-07-01"),
                1: np.datetime64("2019-07-04"),
                2: np.datetime64("2019-07-07"),
                3: np.datetime64("2019-07-08"),
            },
            "departement": {
                0: "Cantal",
                1: "Cantal",
                2: "Cantal",
                3: "Cantal"
            },
            "fwi_mean": {
                0: 1.1,
                1: 13.3,
                2: 0.9,
                3: 2.5
            },
            "fwi_mean_lag1": {
                0: np.nan,
                1: np.nan,
                2: np.nan,
                3: 0.9
            },
            "fwi_mean_lag3": {
                0: np.nan,
                1: 1.1,
                2: 13.3,
                3: np.nan
            },
            "fwi_mean_lag7": {
                0: np.nan,
                1: np.nan,
                2: np.nan,
                3: 1.1
            },
        })
        assert_frame_equal(res, score_v0.add_lags(df, ["fwi_mean"]))

    def test_split_train_test(self):
        X = pd.DataFrame({
            "ffmc_min": [0, 1, 2, 3, 4],
            "strd_max": [1, 1, 3, 3, 5]
        })
        y = pd.Series([0, 0, 0, 1, 1], name="classif_target")
        X_train, X_test, y_train, y_test = score_v0.split_train_test(X, y)
        assert_frame_equal(
            X_train,
            pd.DataFrame({
                "ffmc_min": {
                    4: 4,
                    2: 2,
                    0: 0,
                    3: 3
                },
                "strd_max": {
                    4: 5,
                    2: 3,
                    0: 1,
                    3: 3
                },
            }),
        )
        assert_frame_equal(
            X_test, pd.DataFrame({
                "ffmc_min": {
                    1: 1
                },
                "strd_max": {
                    1: 1
                }
            }))
        assert_series_equal(
            y_train, pd.Series({
                4: 1,
                2: 0,
                0: 0,
                3: 1
            }, name="classif_target"))
        assert_series_equal(y_test, pd.Series({1: 0}, name="classif_target"))

    def test_train_random_forest(self):
        data = load_breast_cancer()
        a, b, c, d = score_v0.split_train_test(data["data"], data["target"])
        rfc = score_v0.train_random_forest(a, b, c, d)
        self.assertEqual(rfc.predict(b[:1]), np.array([1]))
        self.assertEqual(rfc.score(b, d), 0.9736842105263158)

    def test_xgb_model(self):
        data = load_breast_cancer()
        a, b, c, d = score_v0.split_train_test(data["data"], data["target"])
        _, _, preds = score_v0.xgb_model(a,
                                         c,
                                         b,
                                         d,
                                         params={
                                             "min_child_weight": 5,
                                             "eta": 0.1
                                         })
        self.assertEqual(len(preds), 114)
        self.assertEqual(preds[0].round(3), np.float32(0.996))

    def test_pyrorisk(self):
        pr = predict.PyroRisk(which="RF")
        self.assertEqual(pr.model.n_estimators, 500)
        self.assertEqual(pr.model_path, cfg.RFMODEL_ERA5T_PATH)
        res = pr.get_input("2020-05-05")
        self.assertIsInstance(res, pd.DataFrame)
        self.assertEqual(res.shape, (93, 40))
        preds = pr.predict("2020-05-05")
        self.assertEqual(len(preds), 93)
        self.assertEqual(preds["Ardennes"], {
            "score": 0.246,
            "explainability": None
        })


if __name__ == "__main__":
    unittest.main()
