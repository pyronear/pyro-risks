# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal
from sklearn.datasets import load_breast_cancer

from pyro_risks.pipeline import score_v0, predict
from pyro_risks import config as cfg


class ModelsTester(unittest.TestCase):
    def test_prepare_dataset(self):
        df = pd.DataFrame(
            {
                "day": ["2019-07-01", "2019-08-02", "2019-06-12"],
                "departement": ["Aisne", "Cantal", "Savoie"],
                "fires": [0, 5, 10],
                "fwi_mean": [13.3, 0.9, 2.5],
                "ffmc_max": [23, 45.3, 109.0],
            }
        )
        X, y = score_v0.prepare_dataset(df, selected_dep=["Aisne", "Cantal"])
        assert_frame_equal(
            X,
            pd.DataFrame(
                {"fwi_mean": {0: 13.3, 1: 0.9}, "ffmc_max": {0: 23.0, 1: 45.3}}
            ),
            check_like=True,
        )
        assert_series_equal(y, pd.Series([0, 1], name="classif_target"))

    def test_target_correlated_features(self):
        X = pd.DataFrame(
            {
                "str_mean": [2, 3, 4, 0, 0],
                "ffmc_min": [0, 0, 0, 0, 0],
                "isi_mean": [3, 0, 1, 4, 5],
            }
        )
        y = pd.Series(np.array([1, 1, 1, 0, 0]), name="classif_target")
        self.assertEqual(
            score_v0.target_correlated_features(X, y), ["str_mean", "isi_mean"]
        )

    def test_add_lags(self):
        df = pd.DataFrame(
            {
                "day": ["2019-07-01", "2019-07-04", "2019-07-07", "2019-07-08"],
                "departement": ["Cantal", "Cantal", "Cantal", "Cantal"],
                "fwi_mean": [1.1, 13.3, 0.9, 2.5],
            }
        )
        df["day"] = pd.to_datetime(df["day"])
        res = pd.DataFrame(
            {
                "day": {
                    0: np.datetime64("2019-07-01"),
                    1: np.datetime64("2019-07-04"),
                    2: np.datetime64("2019-07-07"),
                    3: np.datetime64("2019-07-08"),
                },
                "departement": {0: "Cantal", 1: "Cantal", 2: "Cantal", 3: "Cantal"},
                "fwi_mean": {0: 1.1, 1: 13.3, 2: 0.9, 3: 2.5},
                "fwi_mean_lag1": {0: np.nan, 1: np.nan, 2: np.nan, 3: 0.9},
                "fwi_mean_lag3": {0: np.nan, 1: 1.1, 2: 13.3, 3: np.nan},
                "fwi_mean_lag7": {0: np.nan, 1: np.nan, 2: np.nan, 3: 1.1},
            }
        )
        assert_frame_equal(res, score_v0.add_lags(df, ["fwi_mean"]))

    def test_split_train_test(self):
        X = pd.DataFrame({"ffmc_min": [0, 1, 2, 3, 4], "strd_max": [1, 1, 3, 3, 5]})
        y = pd.Series([0, 0, 0, 1, 1], name="classif_target")
        X_train, X_test, y_train, y_test = score_v0.split_train_test(X, y)
        assert_frame_equal(
            X_train,
            pd.DataFrame(
                {
                    "ffmc_min": {4: 4, 2: 2, 0: 0, 3: 3},
                    "strd_max": {4: 5, 2: 3, 0: 1, 3: 3},
                }
            ),
        )
        assert_frame_equal(
            X_test, pd.DataFrame({"ffmc_min": {1: 1}, "strd_max": {1: 1}})
        )
        assert_series_equal(
            y_train, pd.Series({4: 1, 2: 0, 0: 0, 3: 1}, name="classif_target")
        )
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
        _, _, preds = score_v0.xgb_model(
            a, c, b, d, params={"min_child_weight": 5, "eta": 0.1}
        )
        self.assertEqual(len(preds), 114)
        self.assertEqual(preds[0].round(3), np.float32(0.996))


    @patch("pyro_risks.datasets.fwi.get_fwi_data_for_predict")
    @patch("pyro_risks.datasets.ERA5.get_data_era5t_for_predict")
    def test_pyrorisk(self, mock_era5, mock_fwi):
        mock_fwi.return_value.get_fwi_from_api.return_value.call_fwi.return_value = Mock()
        mock_era5.return_value.call_era5t.return_value.ERA5T.return_value = Mock()

        fwi_dataset = pd.DataFrame(np.arange(1116).reshape((93, 12)), columns=['code', 'nom', 'latitude', 'longitude', 'bui', 'dc', 'dmc', 'dsr','ffmc', 'fwi', 'isi', 'day'])
        fwi_dataset.nom = ['Aisne', 'Aube', 'Calvados', 'Cantal', 'Eure-et-Loir','Ille-et-Vilaine', 'Jura', 'Landes', 'Loire', 'Loiret','Lot-et-Garonne', 'Meuse', 'Orne', 'Pas-de-Calais', 'Puy-de-Dôme','Bas-Rhin', 'Haut-Rhin', 'Seine-Maritime', 'Yonne','Alpes-de-Haute-Provence', 'Hautes-Alpes', 'Ardèche', 'Ardennes','Ariège', 'Charente-Maritime', 'Corrèze', 'Dordogne', 'Eure','Indre-et-Loire', 'Lozère', 'Nièvre', 'Oise','Pyrénées-Atlantiques', 'Rhône', 'Saône-et-Loire', 'Yvelines','Tarn', 'Tarn-et-Garonne', 'Var', 'Vendée', 'Haute-Vienne','Vosges', 'Allier', 'Alpes-Maritimes', 'Aude', 'Corse-du-Sud',"Côtes-d'Armor", 'Creuse', 'Doubs', 'Finistère', 'Gard', 'Gironde','Indre', 'Isère', 'Marne', 'Haute-Marne', 'Moselle','Hautes-Pyrénées', 'Pyrénées-Orientales', 'Savoie', 'Haute-Savoie','Seine-et-Marne', 'Vaucluse', 'Vienne', 'Val-de-Marne', 'Ain','Aveyron', 'Bouches-du-Rhône', 'Charente', 'Cher', 'Haute-Corse',"Côte-d'Or", 'Drôme', 'Haute-Garonne', 'Gers', 'Hérault','Haute-Loire', 'Loire-Atlantique', 'Lot', 'Maine-et-Loire','Manche', 'Morbihan', 'Nord', 'Haute-Saône', 'Sarthe', 'Somme','Essonne', "Val-d'Oise", 'Loir-et-Cher', 'Mayenne','Meurthe-et-Moselle', 'Deux-Sèvres', 'Territoire de Belfort']
        fwi_dataset.latitude = [46.096153, 49.566666, 46.375   , 43.92857 , 44.06818 , 49.625   ,44.775   , 42.875   , 48.28846 , 43.076923, 44.235294, 48.65625 ,43.53125 , 49.136364, 45.020832, 45.75    , 45.807693, 47.083332,45.325   , 41.8125  , 46.05    , 47.390625, 48.453125, 46.56818 ,45.10294 , 47.18182 , 44.666668, 48.5625  , 49.1     , 48.375   ,48.291668, 44.022728, 43.727272, 44.855263, 47.833332, 42.34375 ,43.346153, 45.13889 , 48.115383, 46.03125 , 47.63889 , 45.886364,44.692307, 43.075   , 43.575   , 48.142857, 46.75    , 47.270832,45.25    , 46.77778 , 44.015625, 47.590908, 45.666668, 47.425   ,47.942307, 44.67857 , 44.425   , 44.5     , 47.392857, 49.022728,48.96875 , 48.175   , 48.857143, 48.958332, 47.807693, 49.020832,47.107143, 50.520832, 49.395832, 48.615383, 50.479168, 45.732143,43.30357 , 42.583332, 45.833332, 47.979168, 45.48077 , 46.609375,49.634617, 48.590908, 49.942307, 43.75    , 44.142857, 47.5     ,49.      , 48.75    , 43.416668, 44.      , 46.75    , 46.576923,48.15    , 47.82143 , 48.9     ]
        fwi_dataset.longitude = [5.38461538,  3.53333333,  3.16071429,  7.07142857,  6.22727273,4.65      ,  4.425     ,  1.5       ,  4.15384615,  2.38461538,2.64705882,  7.625     ,  4.9375    , -0.31818182,  2.66666667,0.20454545, -0.69230769,  2.48333333,  1.9       ,  8.96875   ,2.025     ,  4.78125   , -2.890625  , -0.34090909,  0.77941176,6.31818182,  5.1875    ,  2.25      ,  0.95      ,  1.375     ,-4.14583333,  4.20454545,  0.5       , -0.59210526,  7.27777778,9.1875    ,  1.15384615,  3.80555556,  5.23076923,  6.5       ,6.08333333,  1.22727273,  6.32692308,  0.15      ,  3.4       ,-1.67857143,  1.57692308,  0.70833333,  5.54166667,  5.69444444,-0.75      ,  1.38636364,  4.16666667, -1.625     ,  2.28846154,1.60714286,  0.425     ,  3.5       , -0.60714286, -1.31818182,4.21875   , -0.625     ,  6.14285714,  5.375     , -2.86538462,6.77083333,  3.5       ,  3.14583333,  2.375     ,  0.11538462,2.3125    ,  3.125     , -0.80357143,  2.5       ,  4.66666667,0.20833333,  6.46153846,  4.515625  ,  1.03846154,  2.90909091,2.34615385,  2.125     ,  1.32142857,  7.        ,  2.375     ,2.5       ,  6.22916667,  5.17857143, -1.40625   ,  0.44230769,6.375     ,  3.57142857,  1.8       ]
        fwi_dataset.day = "2020-05-05"
        mock_fwi.return_value = fwi_dataset

        era_dataset = pd.DataFrame(np.arange(20181).reshape((93, 217)), columns=['code', 'nom', 'latitude', 'longitude', 'time', 'u100', 'v100','u10n', 'u10', 'v10n', 'v10', 'fg10', 'd2m', 't2m', 'anor', 'isor','bld', 'blh', 'chnk', 'cdir', 'cape', 'cp', 'crr', 'csf', 'csfr','uvb', 'dctb', 'lgws', 'ewss', 'e', 'fal', 'flsr', 'fsr', 'zust','gwd', 'hcc', 'cvh', 'istl1', 'istl2', 'istl3', 'istl4', 'i10fg','iews', 'ilspf', 'ie', 'inss', 'ishf', 'kx', 'lblt', 'cl', 'dl','licd', 'lict', 'lmld', 'lmlt', 'lshf', 'ltlt', 'lsm', 'lsp','lspf', 'lsrr', 'lsf', 'lssfr', 'lai_hv', 'lai_lv', 'lcc', 'cvl','mx2t', 'mxtpr', 'mbld', 'mcpr', 'mcsr', 'megwss', 'metss', 'mer','mgwd', 'mlspf', 'mlspr', 'mlssr', 'mngwss', 'mntss', 'mper','mror', 'msl', 'mser', 'msr', 'msmr', 'mssror', 'msdrswrf','msdrswrfcs', 'msdwlwrf', 'msdwlwrfcs', 'msdwswrf', 'msdwswrfcs','msdwuvrf', 'mslhf', 'msnlwrf', 'msnlwrfcs', 'msnswrf','msnswrfcs', 'msror', 'msshf', 'mtdwswrf', 'mtnlwrf', 'mtnlwrfcs','mtnswrf', 'mtnswrfcs', 'mtpr', 'dndza', 'mvimd', 'mcc', 'mn2t','mntpr', 'dndzn', 'alnid', 'alnip', 'mgws', 'nsss', 'z', 'pev','ptype', 'ro', 'src', 'skt', 'slor', 'asn', 'rsn', 'sd', 'es','sf', 'smlt', 'stl1', 'stl2', 'stl3', 'stl4', 'slt', 'sdfor','sdor', 'ssro', 'slhf', 'ssr', 'ssrc', 'str', 'strc', 'sp', 'sro','sshf', 'ssrdc', 'ssrd', 'strdc', 'strd', 'tsn', 'tisr', 'tsr','tsrc', 'ttr', 'ttrc', 'tcc', 'tciw', 'tclw', 'tco3', 'tcrw','tcsw', 'tcslw', 'tcw', 'tcwv', 'tp', 'fdir', 'totalx', 'tplb','tplt', 'tvh', 'tvl', 'aluvd', 'aluvp', 'p80.162', 'p79.162','p85.162', 'p82.162', 'p81.162', 'p84.162', 'p87.162', 'p83.162','p86.162', 'p90.162', 'p88.162', 'p73.162', 'p69.162', 'p67.162','p65.162', 'p77.162', 'p75.162', 'p71.162', 'p64.162', 'p59.162','p53.162', 'p92.162', 'p91.162', 'p89.162', 'p74.162', 'p70.162','p68.162', 'p66.162', 'p78.162', 'p76.162', 'p72.162', 'p61.162','p62.162', 'p54.162', 'p60.162', 'p63.162', 'vimd', 'swvl1','swvl2', 'swvl3', 'swvl4', 'deg0l'])
        era_dataset.nom = ['Aisne', 'Aube', 'Calvados', 'Cantal', 'Eure-et-Loir','Ille-et-Vilaine', 'Jura', 'Landes', 'Loire', 'Loiret','Lot-et-Garonne', 'Meuse', 'Orne', 'Pas-de-Calais', 'Puy-de-Dôme','Bas-Rhin', 'Haut-Rhin', 'Seine-Maritime', 'Yonne','Alpes-de-Haute-Provence', 'Hautes-Alpes', 'Ardèche', 'Ardennes','Ariège', 'Charente-Maritime', 'Corrèze', 'Dordogne', 'Eure','Indre-et-Loire', 'Lozère', 'Nièvre', 'Oise','Pyrénées-Atlantiques', 'Rhône', 'Saône-et-Loire', 'Yvelines','Tarn', 'Tarn-et-Garonne', 'Var', 'Vendée', 'Haute-Vienne','Vosges', 'Allier', 'Alpes-Maritimes', 'Aude', 'Corse-du-Sud',"Côtes-d'Armor", 'Creuse', 'Doubs', 'Finistère', 'Gard', 'Gironde','Indre', 'Isère', 'Marne', 'Haute-Marne', 'Moselle','Hautes-Pyrénées', 'Pyrénées-Orientales', 'Savoie', 'Haute-Savoie','Seine-et-Marne', 'Vaucluse', 'Vienne', 'Val-de-Marne', 'Ain','Aveyron', 'Bouches-du-Rhône', 'Charente', 'Cher', 'Haute-Corse',"Côte-d'Or", 'Drôme', 'Haute-Garonne', 'Gers', 'Hérault','Haute-Loire', 'Loire-Atlantique', 'Lot', 'Maine-et-Loire','Manche', 'Morbihan', 'Nord', 'Haute-Saône', 'Sarthe', 'Somme','Essonne', "Val-d'Oise", 'Loir-et-Cher', 'Mayenne','Meurthe-et-Moselle', 'Deux-Sèvres', 'Territoire de Belfort']
        era_dataset.latitude = [46.096153, 49.566666, 46.375   , 43.92857 , 44.06818 , 49.625   ,44.775   , 42.875   , 48.28846 , 43.076923, 44.235294, 48.65625 ,43.53125 , 49.136364, 45.020832, 45.75    , 45.807693, 47.083332,45.325   , 41.8125  , 46.05    , 47.390625, 48.453125, 46.56818 ,45.10294 , 47.18182 , 44.666668, 48.5625  , 49.1     , 48.375   ,48.291668, 44.022728, 43.727272, 44.855263, 47.833332, 42.34375 ,43.346153, 45.13889 , 48.115383, 46.03125 , 47.63889 , 45.886364,44.692307, 43.075   , 43.575   , 48.142857, 46.75    , 47.270832,45.25    , 46.77778 , 44.015625, 47.590908, 45.666668, 47.425   ,47.942307, 44.67857 , 44.425   , 44.5     , 47.392857, 49.022728,48.96875 , 48.175   , 48.857143, 48.958332, 47.807693, 49.020832,47.107143, 50.520832, 49.395832, 48.615383, 50.479168, 45.732143,43.30357 , 42.583332, 45.833332, 47.979168, 45.48077 , 46.609375,49.634617, 48.590908, 49.942307, 43.75    , 44.142857, 47.5     ,49.      , 48.75    , 43.416668, 44.      , 46.75    , 46.576923,48.15    , 47.82143 , 48.9     ]
        era_dataset.longitude = [5.38461538,  3.53333333,  3.16071429,  7.07142857,  6.22727273,4.65      ,  4.425     ,  1.5       ,  4.15384615,  2.38461538,2.64705882,  7.625     ,  4.9375    , -0.31818182,  2.66666667,0.20454545, -0.69230769,  2.48333333,  1.9       ,  8.96875   ,2.025     ,  4.78125   , -2.890625  , -0.34090909,  0.77941176,6.31818182,  5.1875    ,  2.25      ,  0.95      ,  1.375     ,-4.14583333,  4.20454545,  0.5       , -0.59210526,  7.27777778,9.1875    ,  1.15384615,  3.80555556,  5.23076923,  6.5       ,6.08333333,  1.22727273,  6.32692308,  0.15      ,  3.4       ,-1.67857143,  1.57692308,  0.70833333,  5.54166667,  5.69444444,-0.75      ,  1.38636364,  4.16666667, -1.625     ,  2.28846154,1.60714286,  0.425     ,  3.5       , -0.60714286, -1.31818182,4.21875   , -0.625     ,  6.14285714,  5.375     , -2.86538462,6.77083333,  3.5       ,  3.14583333,  2.375     ,  0.11538462,2.3125    ,  3.125     , -0.80357143,  2.5       ,  4.66666667,0.20833333,  6.46153846,  4.515625  ,  1.03846154,  2.90909091,2.34615385,  2.125     ,  1.32142857,  7.        ,  2.375     ,2.5       ,  6.22916667,  5.17857143, -1.40625   ,  0.44230769,6.375     ,  3.57142857,  1.8       ]
        era_dataset.time = "2020-05-05"
        mock_era5.return_value = era_dataset

        pr = predict.PyroRisk(which="RF")
        self.assertEqual(pr.model.n_estimators, 500)
        self.assertEqual(pr.model_path, cfg.RFMODEL_ERA5T_PATH)

        res = pr.get_input("2020-05-05")

        self.assertIsInstance(res, pd.DataFrame)
        self.assertEqual(res.shape, (93, 40))
        preds = pr.predict("2020-05-05")
        self.assertEqual(len(preds), 93)
        self.assertEqual(preds["Ardennes"], {"score": 0.246, "explainability": None})


if __name__ == "__main__":
    unittest.main()
