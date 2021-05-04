# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

ZONE_VAR = "departement"

DATE_VAR = "day"

TARGET = "fires"

PIPELINE_ERA5T_VARS = [
    "strd_min",
    "isi_min",
    "strd_max",
    "d2m_mean",
    "lai_hv_mean",
    "str_mean",
    "ffmc_mean",
    "strd_mean",
    "swvl1_mean",
    "asn_min",
    "fwi_mean",
    "asn_std",
    "ssr_mean",
    "str_max",
    "d2m_min",
    "rsn_std",
    "ssrd_min",
    "isi_mean",
    "ssrd_mean",
    "isi_max",
    "ffmc_max",
    "ffmc_min",
    "ssr_min",
    "str_min",
    "ffmc_std",
]

MODEL_ERA5T_VARS = [
    "str_max",
    "str_mean",
    "ffmc_min",
    "str_min",
    "ffmc_mean",
    "str_mean_lag1",
    "str_max_lag1",
    "str_min_lag1",
    "isi_min",
    "ffmc_min_lag1",
    "isi_mean",
    "ffmc_mean_lag1",
    "ffmc_std",
    "ffmc_max",
    "isi_min_lag1",
    "isi_mean_lag1",
    "ffmc_max_lag1",
    "asn_std",
    "strd_max",
    "ssrd_min",
    "strd_mean",
    "isi_max",
    "strd_min",
    "d2m_min",
    "asn_min",
    "ssr_min",
    "ffmc_min_lag3",
    "ffmc_std_lag1",
    "lai_hv_mean_lag7",
    "str_max_lag3",
    "str_mean_lag3",
    "rsn_std_lag1",
    "fwi_mean",
    "ssr_mean",
    "ssrd_mean",
    "swvl1_mean",
    "rsn_std_lag3",
    "isi_max_lag1",
    "d2m_mean",
    "rsn_std",
]

SELECTED_DEP = [
    "Aisne",
    "Alpes-Maritimes",
    "Ardèche",
    "Ariège",
    "Aude",
    "Aveyron",
    "Cantal",
    "Eure",
    "Eure-et-Loir",
    "Gironde",
    "Haute-Corse",
    "Hautes-Pyrénées",
    "Hérault",
    "Indre",
    "Landes",
    "Loiret",
    "Lozère",
    "Marne",
    "Oise",
    "Pyrénées-Atlantiques",
    "Pyrénées-Orientales",
    "Sarthe",
    "Somme",
    "Yonne",
]

LAG_ERA5T_VARS = ["_".join(x.split("_")[:-1]) for x in MODEL_ERA5T_VARS if "_lag" in x]

RESAMPLING_TECHNIQUE = "SMOTE"

TEST_SIZE = 0.2

RANDOM_STATE = 42

RF_PARAMS = {
    "n_estimators": 500,
    "min_samples_leaf": 10,
    "max_features": "sqrt",
    "class_weight": "balanced",
    "criterion": "gini",
    "random_state": 10,
    "n_jobs": -1,
    "verbose": 3,
}

XGB_PARAMS = {
    "n_estimators": 1000,
    "max_depth": 10,
    "learning_rate": 0.01,
    "min_child_weight": 10,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "binary:logistic",
    "random_state": 10,
    "n_jobs": -1,
    "verbosity": 2,
}


XGB_FIT_PARAMS = {
    "early_stopping_rounds": 50,
    "eval_metric": ["logloss", "aucpr"],
}
