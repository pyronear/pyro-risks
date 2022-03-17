# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import Union, Optional
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve
from sklearn.utils import estimator_html_repr
from pyro_risks.models import xgb_pipeline, rf_pipeline, discretizer
from pyro_risks.pipeline.load import load_dataset
from datetime import datetime
import imblearn.pipeline as pp
import pyro_risks.config as cfg

import sys
import pandas as pd
import numpy as np

import os
import time
import json
import joblib

__all__ = ["calibrate_pipeline", "save_pipeline", "train_pipeline"]


def calibrate_pipeline(
    y_test: Union[pd.Series, np.ndarray],
    y_scores: Union[pd.Series, np.ndarray],
    ignore_prints: Optional[bool] = False,
) -> np.float64:
    """
    Calibrate Classification Pipeline.

    Args:
        y_test: Binary test target.
        y_scores: Predicted probabilities from the test set.
        ignore_prints: Whether to print results. Defaults to False.

    Returns:
        Threshold maximizing the f1-score.
    """
    precision, recall, thresholds = precision_recall_curve(y_test, y_scores[:, 1])
    fscore = (2 * precision * recall) / (precision + recall)
    ix = np.argmax(fscore)

    if not ignore_prints:
        print(f"Best Threshold={thresholds[ix]}, F-Score={fscore[ix]}")

    return thresholds[ix]


def save_pipeline(
    pipeline: pp.Pipeline,
    model: str,
    optimal_threshold: np.float64,
    destination: Optional[str] = None,
    ignore_html: Optional[bool] = False,
) -> None:
    """
    Serialize pipeline.

    Args:
        pipeline: imbalanced-learn preprocessing pipeline.
        model: model name.
        optimal_threshold: model calibration optimal threshold.
        destination: folder where the pipeline should be saved. Defaults to 'cfg.MODEL_REGISTRY'.
        ignore_html: Persist pipeline html description. Defaults to False.
    """
    threshold = {"threshold": float(optimal_threshold)}
    registry = cfg.MODEL_REGISTRY if destination is None else destination
    pipeline_fname = f"{model}.joblib"
    threshold_fname = f"{model}_threshold.json"
    html_fname = f"{model}_pipeline.html"

    if not os.path.exists(registry):
        os.makedirs(registry)

    joblib.dump(pipeline, os.path.join(registry, pipeline_fname))

    with open(registry + "/" + threshold_fname, "w") as file:
        json.dump(threshold, file)

    if not ignore_html:
        with open(registry + "/" + html_fname, "w") as file:
            file.write(estimator_html_repr(pipeline))


def train_pipeline(
    X: pd.DataFrame,
    y: pd.Series,
    model: str,
    pipeline: Optional[pp.Pipeline] = None,
    destination: Optional[str] = None,
    ignore_prints: Optional[bool] = False,
    ignore_html: Optional[bool] = False,
) -> None:
    """
    Train a classification pipeline.

    Args:
        X: Training dataset features pd.DataFrame.
        y: Training dataset target pd.Series.
        model: model name.
        pipeline: imbalanced-learn preprocessing pipeline. Defaults to None.
        destination: folder where the pipeline should be saved. Defaults to 'cfg.MODEL_REGISTRY'.
        ignore_prints: Whether to print results. Defaults to False.
        ignore_html: Persist pipeline html description. Defaults to False.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=cfg.TEST_SIZE, random_state=cfg.RANDOM_STATE
    )

    vdiscretizer = np.vectorize(discretizer)

    if model == "RF":
        rf_pipeline.fit(X_train, y_train)
        y_scores = rf_pipeline.predict_proba(X_test)
        optimal_threshold = calibrate_pipeline(
            y_test=vdiscretizer(y_test), y_scores=y_scores, ignore_prints=ignore_prints
        )
        save_pipeline(
            pipeline=rf_pipeline,
            model=model,
            optimal_threshold=optimal_threshold,
            destination=destination,
            ignore_html=ignore_html,
        )

    elif model == "XGBOOST":
        xgb_pipeline.fit(
            X_train, y_train, xgboost__eval_metric=cfg.XGB_FIT_PARAMS["eval_metric"]
        )
        y_scores = xgb_pipeline.predict_proba(X_test)
        optimal_threshold = calibrate_pipeline(
            y_test=vdiscretizer(y_test), y_scores=y_scores, ignore_prints=ignore_prints
        )
        save_pipeline(
            pipeline=xgb_pipeline,
            model=model,
            optimal_threshold=optimal_threshold,
            destination=destination,
            ignore_html=ignore_html,
        )

    elif model not in ["RF", "XGBOOST"] and pipeline is not None:
        pipeline.fit(X_train, y_train)
        y_scores = pipeline.predict_proba(X_test)
        optimal_threshold = calibrate_pipeline(
            y_test=vdiscretizer(y_test), y_scores=y_scores, ignore_prints=ignore_prints
        )
        save_pipeline(
            pipeline=pipeline,
            model=model,
            optimal_threshold=optimal_threshold,
            destination=destination,
            ignore_html=ignore_html,
        )
