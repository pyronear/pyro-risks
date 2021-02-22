# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from typing import List, Union, Optional, Dict, Tuple
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve
from sklearn.utils import estimator_html_repr
from pyro_risks.models import xgb_pipeline, rf_pipeline, discretizer
from pyro_risks.datasets import MergedEraFwiViirs

from datetime import datetime
import imblearn.pipeline as pp
import pyro_risks.config as cfg

import sys
import pandas as pd
import numpy as np

import os
import time
import joblib

__all__ = ["calibrate_pipeline", "save_pipeline", "train_pipeline"]


def calibrate_pipeline(
    y_test: Union[pd.Series, np.ndarray],
    y_scores: Union[pd.Series, np.ndarray],
    ignore_prints: Optional[bool] = False,
) -> np.float64:
    """Calibrate Classification Pipeline.

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
):
    """Serialize pipeline.

    Args:
        pipeline: imbalanced-learn preprocessing pipeline.
        model: model name.
        optimal_threshold: model calibration optimal threshold.
        destination: folder where the pipeline should be saved. Defaults to 'cfg.MODEL_REGISTRY'.
        ignore_html: Persist pipeline html description. Defaults to False.
    """

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    optimal_threshold = str(round(optimal_threshold, 4)).replace(".", "-")
    registry = cfg.MODEL_REGISTRY if destination is None else destination
    pipeline_fname = f"{model}_{optimal_threshold}_{timestamp}.joblib"
    html_fname = f"{model}_{optimal_threshold}_{timestamp}.html"

    if not os.path.exists(registry):
        os.makedirs(registry)

    joblib.dump(pipeline, os.path.join(registry, pipeline_fname))

    if not ignore_html:
        with open(registry + "/" + html_fname, "w") as f:
            f.write(estimator_html_repr(pipeline))


def train_pipeline(
    X: pd.DataFrame,
    y: pd.Series,
    model: str,
    pipeline: Optional[pp.Pipeline] = None,
    destination: Optional[str] = None,
    ignore_prints: Optional[bool] = False,
    ignore_html: Optional[bool] = False,
):
    """Train a classification pipeline.

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
            X_train,
            y_train,
            xgboost__eval_metric=cfg.XGB_FIT_PARAMS["eval_metric"],
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


def main(args):
    usecols = [cfg.DATE_VAR, cfg.ZONE_VAR, cfg.TARGET] + cfg.PIPELINE_ERA5T_VARS
    pipeline_vars = [cfg.DATE_VAR, cfg.ZONE_VAR] + cfg.PIPELINE_ERA5T_VARS
    df = pd.read_csv(cfg.ERA5T_VIIRS_PIPELINE, usecols=usecols)
    df["day"] = df["day"].apply(
        lambda x: datetime.strptime(str(x), "%Y-%m-%d") if not pd.isnull(x) else x
    )
    X = df[pipeline_vars]
    y = df[cfg.TARGET]
    train_pipeline(
        X=X,
        y=y,
        model=args.model,
        destination=args.destination,
        ignore_prints=args.ignore_prints,
        ignore_html=args.ignore_html,
    )


def parse_args(args):
    import argparse

    parser = argparse.ArgumentParser(
        description="Pyrorisks Classification Pipeline Training",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--model", default="RF", help="Classification Pipeline name RF or XGBOOST."
    )
    parser.add_argument(
        "--destination",
        default=None,
        help="Destination folder for persisting pipeline.",
    )
    parser.add_argument(
        "--ignore_prints",
        dest="ignore_prints",
        action="store_true",
        help="Whether to print results. Defaults to False.",
    )
    parser.add_argument(
        "--prints",
        dest="ignore_prints",
        action="store_false",
        help="Whether to print results. Defaults to False.",
    )
    parser.set_defaults(ignore_prints=True)

    parser.add_argument(
        "--ignore_html",
        dest="ignore_html",
        action="store_true",
        help="Persist pipeline html description. Defaults to False.",
    )
    parser.add_argument(
        "--html",
        dest="ignore_html",
        action="store_false",
        help="Persist pipeline html description. Defaults to False.",
    )
    parser.set_defaults(ignore_html=True)
    return parser.parse_args(args)


if __name__ == "__main__":

    args = parse_args(sys.argv[1:])
    main(args)
