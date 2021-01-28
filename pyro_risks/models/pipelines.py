from imblearn.pipeline import Pipeline
from .transformers import (
    TargetDiscretizer,
    CategorySelector,
    Imputer,
    LagTransformer,
    FeatureSubsetter,
)
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

import pyro_risks.config as cfg

__all__ = ["xgb_pipeline", "rf_pipeline"]

# pipeline base steps definition
base_steps = [
    (
        "filter_dep",
        CategorySelector(variable=cfg.ZONE_VAR, category=cfg.SELECTED_DEP),
    ),
    (
        "add_lags",
        LagTransformer(
            date_column=cfg.DATE_VARS,
            zone_column=cfg.ZONE_VAR,
            columns=cfg.LAG_ERA5T_VARS,
        ),
    ),
    ("imputer", Imputer(columns=cfg.LAG_ERA5T_VARS, fill_value=-1)),
    ("binarize_target", TargetDiscretizer(discretizer=lambda x: 1 if x > 0 else 0)),
    ("subset_features", FeatureSubsetter(columns=cfg.MODEL_ERA5T_VARS)),
]

# Add estimator to base step lists
xgb_steps = [*base_steps, ("xgboost", XGBClassifier(cfg.XGB_PARAMS))]
rf_steps = [*base_steps, ("random_forest", RandomForestClassifier(cfg.RF_PARAMS))]

# Define sklearn / imblearn pipelines
xgb_pipeline = Pipeline(xgb_steps)
rf_pipeline = Pipeline(rf_steps)
