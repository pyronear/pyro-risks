from typing import List, Union, Optional, Dict, Tuple
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve
from sklearn.utils import estimator_html_repr
from pyro_risks.models import xgb_pipeline, rf_pipeline
from pyro_risks.datasets import MergedEraFwiViirs

import imblearn.pipeline as pp
import pyro_risks.config as cfg

import pandas as pd
import numpy as np

import os
import time
import joblib


def calibrate_pipeline(y_test: Union[pd.Series, np.ndarray],
                       y_score: Union[pd.Series, np.ndarray],
                       ignore_prints: Optional[bool] = False) -> np.float64:
    """Calibrate Classification Pipeline.

    Args:
        y_test: Binary test target.
        y_score: Predicted probabilities from the test set.
        ignore_prints: Whether to print results. Defaults to False.

    Returns:
        Threshold maximizing the f1-score.
    """

    precision, recall, thresholds = precision_recall_curve(y_test, y_score)
    fscore = (2 * precision * recall) / (precision + recall)
    ix = np.argmax(fscore)

    if not ignore_prints:
        print(f"Best Threshold={thresholds[ix]}, F-Score={fscore[ix]}")

    return thresholds[ix]


def save_pipeline(pipeline: pp.Pipeline,
                  model: str,
                  optimal_threshold: np.float64,
                  ignore_html: Optional[bool] = False):
    """Serialize pipeline.

    Args:
        pipeline: imbalanced-learn preprocessing pipeline.
        model: model name.
        optimal_threshold: model calibration optimal threshold.
        ignore_html: Persist pipeline html description. Defaults to False.
    """

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    pipeline_fname = f"{model}_{optimal_threshold}_{timestamp}.joblib"
    html_fname = f"{model}_{optimal_threshold}_{timestamp}.html"

    if not os.path.exists(cfg.MODEL_REGISTRY):
        os.makedirs(cfg.MODEL_REGISTRY)
        joblib.dump(pipeline, os.path.join(cfg.MODEL_REGISTRY, pipeline_fname))

    if not ignore_html:
        with open(html_fname, "w") as f:
            f.write(estimator_html_repr(pipeline))


def train_pipeline(X: pd.DataFrame,
                   y: pd.Series,
                   model: str,
                   pipeline: Optional[pp.Pipeline] = None,
                   ignore_prints: Optional[bool] = False,
                   ignore_html: Optional[bool] = False):
    """Train a classification pipeline.

    Args:
        X: Training dataset features pd.DataFrame.
        y: Training dataset target pd.Series.
        model: model name.
        pipeline: imbalanced-learn preprocessing pipeline. Defaults to None.
        ignore_prints: Whether to print results. Defaults to False.
        ignore_html: Persist pipeline html description. Defaults to False.
    """

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=cfg.TEST_SIZE, random_state=cfg.RANDOM_STATE)

    if model == "RF":
        rf_pipeline.fit(X_train, y_train)
        y_score = rf_pipeline.predict_proba(X_test)
        optimal_threshold = calibrate_pipeline(y_test, y_score[:, 1],
                                               ignore_prints)
        save_pipeline(rf_pipeline, model, optimal_threshold, ignore_html)

    elif model == "XGBOOST":
        xgb_pipeline.fit(X_train, y_train)
        y_score = rf_pipeline.predict_proba(X_test)
        optimal_threshold = calibrate_pipeline(y_test, y_score[:, 1],
                                               ignore_prints)
        save_pipeline(xgb_pipeline, model, optimal_threshold, ignore_html)

    elif model not in ["RF", "XGBOOST"] and pipeline is not None:
        pipeline.fit(X_train, y_train)
        y_score = pipeline.predict_proba(X_test)
        optimal_threshold = calibrate_pipeline(y_test, y_score[:, 1],
                                               ignore_prints)
        save_pipeline(pipeline, model, optimal_threshold, ignore_html)


def main(args):
    df = MergedEraFwiViirs()
    X = df.drop([cfg.TARGET])
    y = df[cfg.TARGET]
    train_pipeline(X=X,
                   y=y,
                   model=args.model,
                   ignore_prints=args.ignore_html,
                   ignore_html=args.ignore_html)


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
        description='Pyrorisks Classification Pipeline Training',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--model',
                        default='RF',
                        help='Classification Pipeline name RF or XGBOOST.')
    parser.add_argument('--ignore_prints',
                        default=False,
                        help='Whether to print results. Defaults to False.')
    parser.add_argument(
        '--ignore_html',
        default=False,
        help='Persist pipeline html description. Defaults to False.')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = parse_args()
    main(args)
