# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

import unittest
import numpy as np
import pandas as pd

from pandas.testing import assert_frame_equal, assert_series_equal

from pyro_risks.models import (
    TargetDiscretizer,
    CategorySelector,
    Imputer,
    LagTransformer,
    FeatureSelector,
    FeatureSubsetter,
)


class TransformersTester(unittest.TestCase):
    def test_target_discretizer(self):
        td = TargetDiscretizer(discretizer=lambda x: 1 if x > 0 else 0)
        df = pd.DataFrame(
            {
                "day": ["2019-07-01", "2019-08-02", "2019-06-12"],
                "departement": ["Aisne", "Cantal", "Savoie"],
                "fires": [0, 5, 10],
                "fwi_mean": [13.3, 0.9, 2.5],
                "ffmc_max": [23, 45.3, 109.0],
            }
        )
        X = df.drop(columns=["fires"])
        y = df["fires"]

        Xr, yr = td.fit_resample(X, y)
        assert_series_equal(yr, pd.Series([0, 1, 1], name="fires"))
        assert_frame_equal(Xr, X)
        self.assertRaises(TypeError, TargetDiscretizer, [0, 1])

    def test_category_selector(self):
        cs = CategorySelector(variable="departement", category=["Aisne", "Cantal"])
        df = pd.DataFrame(
            {
                "day": ["2019-07-01", "2019-08-02", "2019-06-12"],
                "departement": ["Aisne", "Cantal", "Savoie"],
                "fires": [0, 5, 10],
                "fwi_mean": [13.3, 0.9, 2.5],
                "ffmc_max": [23, 45.3, 109.0],
            }
        )
        X = df.drop(columns=["fires"])
        y = df["fires"]

        Xr, yr = cs.fit_resample(X, y)

        self.assertRaises(TypeError, CategorySelector, "departement", 0)
        assert_frame_equal(Xr, X[X["departement"].isin(["Aisne", "Cantal"])])
        assert_series_equal(yr, y[X["departement"].isin(["Aisne", "Cantal"])])

    # pylint: disable=R0201
    def test_imputer(self):
        imp = Imputer(strategy="median", columns=["fwi_mean"])
        df = pd.DataFrame(
            {
                "fires": [0, 5, 10],
                "fwi_mean": [13.3, np.nan, 2.5],
                "ffmc_max": [23, np.nan, 109.0],
            }
        )

        X = df.drop(columns=["fires"])
        y = df["fires"]

        imp.fit(X, y)

        XT = imp.transform(X)

        assert_frame_equal(
            XT,
            pd.DataFrame(
                {
                    "fwi_mean": [13.3, 7.9, 2.5],
                    "ffmc_max": [23, np.nan, 109.0],
                }
            ),
        )

    def test_lag_transformer(self):
        lt = LagTransformer(
            date_column="date", zone_column="departement", columns=["fwi_mean"]
        )
        df = pd.DataFrame(
            {
                "date": [
                    np.datetime64("2019-07-01"),
                    np.datetime64("2019-07-04"),
                    np.datetime64("2019-07-07"),
                    np.datetime64("2019-07-08"),
                ],
                "departement": ["Cantal", "Cantal", "Cantal", "Cantal"],
                "fwi_mean": [1.1, 13.3, 0.9, 2.5],
                "fires": [0, 5, 10, 10],
            }
        )
        res = pd.DataFrame(
            {
                "date": [
                    np.datetime64("2019-07-01"),
                    np.datetime64("2019-07-04"),
                    np.datetime64("2019-07-07"),
                    np.datetime64("2019-07-08"),
                ],
                "departement": ["Cantal", "Cantal", "Cantal", "Cantal"],
                "fwi_mean": [1.1, 13.3, 0.9, 2.5],
                "fwi_mean_lag1": [np.nan, np.nan, np.nan, 0.9],
                "fwi_mean_lag3": [np.nan, 1.1, 13.3, np.nan],
                "fwi_mean_lag7": [np.nan, np.nan, np.nan, 1.1],
            }
        )

        X = df.drop(columns=["fires"])
        y = df["fires"]

        lt.fit(X, y)

        X = lt.transform(X)

        pd.DataFrame(
            {
                "day": ["2019-07-01", "2019-08-02", "2019-06-12"],
                "departement": ["Aisne", "Cantal", "Savoie"],
                "fwi_mean": [13.3, 0.9, 2.5],
                "ffmc_max": [23, 45.3, 109.0],
            }
        )

        assert_frame_equal(res, X)
        self.assertRaises(
            TypeError,
            LagTransformer.transform,
            pd.DataFrame(
                {
                    "day": ["2019-07-01", "2019-08-02", "2019-06-12"],
                    "departement": ["Aisne", "Cantal", "Savoie"],
                    "fwi_mean": [13.3, 0.9, 2.5],
                    "ffmc_max": [23, 45.3, 109.0],
                }
            ),
        )

    # pylint: disable=R0201
    def test_feature_selector(self):
        fs = FeatureSelector(
            exclude=["date", "department"], method="pearson", threshold=0.15
        )
        df = pd.DataFrame(
            {
                "date": [
                    np.datetime64("2019-07-01"),
                    np.datetime64("2019-07-04"),
                    np.datetime64("2019-07-06"),
                    np.datetime64("2019-07-07"),
                    np.datetime64("2019-07-08"),
                ],
                "departement": ["Cantal", "Cantal", "Cantal", "Cantal", "Cantal"],
                "str_mean": [2, 3, 4, 0, 0],
                "ffmc_min": [0, 0, 0, 0, 0],
                "isi_mean": [3, 0, 1, 4, 5],
                "fires": [1, 1, 1, 0, 0],
            }
        )

        X = df.drop(columns=["fires"])
        y = df["fires"]

        fs.fit(X, y)
        X = fs.transform(X)

        res = pd.DataFrame(
            {
                "str_mean": [2, 3, 4, 0, 0],
                "isi_mean": [3, 0, 1, 4, 5],
            }
        )

        assert_frame_equal(res, X)

    # pylint: disable=R0201
    def test_feature_subsetter(self):
        fs = FeatureSubsetter(columns=["date", "departement", "str_mean"])
        df = pd.DataFrame(
            {
                "date": [
                    np.datetime64("2019-07-01"),
                    np.datetime64("2019-07-04"),
                    np.datetime64("2019-07-06"),
                    np.datetime64("2019-07-07"),
                    np.datetime64("2019-07-08"),
                ],
                "departement": ["Cantal", "Cantal", "Cantal", "Cantal", "Cantal"],
                "str_mean": [2, 3, 4, 0, 0],
                "ffmc_min": [0, 0, 0, 0, 0],
                "isi_mean": [3, 0, 1, 4, 5],
                "fires": [1, 1, 1, 0, 0],
            }
        )

        X = df.drop(columns=["fires"])
        y = df["fires"]

        fs.fit(X, y)
        X = fs.transform(X)

        res = pd.DataFrame(
            {
                "date": [
                    np.datetime64("2019-07-01"),
                    np.datetime64("2019-07-04"),
                    np.datetime64("2019-07-06"),
                    np.datetime64("2019-07-07"),
                    np.datetime64("2019-07-08"),
                ],
                "departement": ["Cantal", "Cantal", "Cantal", "Cantal", "Cantal"],
                "str_mean": [2, 3, 4, 0, 0],
            }
        )

        assert_frame_equal(res, X)


if __name__ == "__main__":
    unittest.main()
