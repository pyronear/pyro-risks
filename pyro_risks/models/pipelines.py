# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from imblearn.pipeline import Pipeline
from .transformers import (
    TargetDiscretizer,
    CategorySelector,
    Imputer,
    LagTransformer,
    FeatureSubsetter,
)
from .utils import discretizer

from sklearn.ensemble import RandomForestClassifier

# from xgboost import XGBClassifier

import pyro_risks.config as cfg

__all__ = ["rf_pipeline"]  # "xgb_pipeline",

# pipeline base steps definition
base_steps = [
    (
        "filter_dep",
        CategorySelector(variable=cfg.ZONE_VAR, category=cfg.SELECTED_DEP),
    ),
    (
        "add_lags",
        LagTransformer(
            date_column=cfg.DATE_VAR,
            zone_column=cfg.ZONE_VAR,
            columns=cfg.LAG_ERA5T_VARS,
        ),
    ),
    ("imputer", Imputer(columns=cfg.MODEL_ERA5T_VARS, strategy="median")),
    ("binarize_target", TargetDiscretizer(discretizer=discretizer)),
    ("subset_features", FeatureSubsetter(columns=cfg.MODEL_ERA5T_VARS)),
]

# Add estimator to base step lists
# xgb_steps = [*base_steps, ("xgboost", XGBClassifier(**cfg.XGB_PARAMS))]
rf_steps = [*base_steps, ("random_forest", RandomForestClassifier(**cfg.RF_PARAMS))]

# Define sklearn / imblearn pipelines
# xgb_pipeline = Pipeline(xgb_steps)
rf_pipeline = Pipeline(rf_steps)
