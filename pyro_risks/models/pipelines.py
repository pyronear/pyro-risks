# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.
from imblearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from .transformers import (
    TargetDiscretizer,
    CategorySelector,
    Imputer,
    LagTransformer,
    FeatureSubsetter,
    CastTypesToNumeric,
    ResetIndex,
    CustomSMOTE,
    DecodeLabelsAndTimestamps,
)
from .utils import discretizer

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

import pyro_risks.config as cfg

__all__ = ["xgb_pipeline", "rf_pipeline"]
label_encoder = LabelEncoder()
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
            resampling=cfg.RESAMPLING_TECHNIQUE,
        ),
    ),
    ("imputer", Imputer(columns=cfg.MODEL_ERA5T_VARS, strategy="median")),
    ("binarize_target", TargetDiscretizer(discretizer=discretizer)),
    ("subset_features", FeatureSubsetter(columns=cfg.MODEL_ERA5T_VARS)),
]

# Preprocessing steps
smote_step = [
    ("cast_types_to_numeric", CastTypesToNumeric(label_encoder=label_encoder)),
    ("smote_imputer", Imputer(strategy="median", columns=["asn_std", "rsn_std"])),
    ("reset_index", ResetIndex()),
    ("binarize_target_pre_SMOTE", TargetDiscretizer(discretizer=discretizer)),
    (
        "smote",
        CustomSMOTE(
            sampling_strategy="not majority",
            random_state=cfg.RANDOM_STATE,
            columns=[cfg.DATE_VAR]
            + [cfg.ZONE_VAR]
            + cfg.PIPELINE_ERA5T_VARS
            + ["is_original_data"],
        ),
    ),
    ("reset_index_post_SMOTE", ResetIndex()),
    ("uncast_types", DecodeLabelsAndTimestamps(label_encoder=label_encoder)),
]

# Add estimator to base step lists
xgb_steps = [*base_steps, ("xgboost", XGBClassifier(**cfg.XGB_PARAMS))]
rf_steps = [*base_steps, ("random_forest", RandomForestClassifier(**cfg.RF_PARAMS))]

# Define sklearn / imblearn pipelines
preprocessing_pipeline = Pipeline(smote_step)
xgb_pipeline = Pipeline(rf_steps)
rf_pipeline = Pipeline(rf_steps)
