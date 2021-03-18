# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from typing import Union, Optional
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from plot_metric.functions import BinaryClassification
from pyro_risks.models import discretizer
from pyro_risks.load import load_dataset
import sys
import os
import json
import joblib

import matplotlib.pyplot as plt
import imblearn.pipeline as pp
import pyro_risks.config as cfg

import pandas as pd
import numpy as np

__all__ = [
    "save_classification_reports",
    "save_classification_plots",
    "evaluate_pipeline",
]


def save_classification_reports(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    prefix: Optional[str] = None,
    destination: Optional[str] = None,
):
    """
    Build and save binary classification metrics reports.

    Args:
        y_true: Ground truth (correct) labels.
        y_pred: Predicted labels, as returned by a calibrated classifier.
        prefix: Classification report prefix i.e. pipeline name. Defaults to None.
        destination: Folder where the report should be saved. Defaults to ``METADATA_REGISTRY``.
    """
    destination = cfg.METADATA_REGISTRY if destination is None else destination
    fname = (
        "classification_report" if prefix is None else prefix + "_classification_report"
    )
    json_report_path = os.path.join(destination, fname + ".json")
    csv_report_path = os.path.join(destination, fname + ".csv")

    report = classification_report(y_true, y_pred, output_dict=True)

    # JSON report for tracking metrics
    with open(json_report_path, "w") as fp:
        json.dump(obj=report, fp=fp)

    # CSV report for plotting classification report
    report.pop("accuracy")
    pd.DataFrame(report).transpose().round(3).to_csv(csv_report_path)

    print(classification_report(y_true, y_pred))


def save_classification_plots(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    threshold: np.float64,
    prefix: Optional[str] = None,
    destination: Optional[str] = None,
):
    """
    Build and save binary classification performance evaluation plots.

    Args:
        y_true: Ground truth (correct) labels.
        y_pred: Predicted probabilities of the positive class returned by a classifier.
        threshold: Classification pipeline optimal threshold.
        prefix: Classification plots prefix i.e. pipeline name. Defaults to None.
        destination: Folder where the report should be saved. Defaults to ``METADATA_REGISTRY``.
    """
    destination = cfg.METADATA_REGISTRY if destination is None else destination
    fname = (
        "classification_plots.png"
        if prefix is None
        else prefix + "_classification_plots.png"
    )
    path = os.path.join(destination, fname)

    bc = BinaryClassification(y_true, y_proba, labels=["No fire", "Fire"])

    plt.figure(figsize=(15, 10))
    plt.subplot2grid(shape=(2, 6), loc=(0, 0), colspan=2)
    bc.plot_roc_curve(threshold=threshold)
    plt.subplot2grid((2, 6), (0, 2), colspan=2)
    bc.plot_precision_recall_curve(threshold=threshold)
    plt.subplot2grid((2, 6), (0, 4), colspan=2)
    bc.plot_class_distribution(threshold=threshold)
    plt.subplot2grid((2, 6), (1, 1), colspan=2)
    bc.plot_confusion_matrix(threshold=threshold)
    plt.subplot2grid((2, 6), (1, 3), colspan=2)
    bc.plot_confusion_matrix(threshold=threshold, normalize=True)

    plt.savefig(path)


def evaluate_pipeline(
    X: pd.DataFrame,
    y: pd.Series,
    pipeline: Optional[Union[pp.Pipeline, str]],
    threshold: np.float64,
    prefix: Optional[str] = None,
    destination: Optional[str] = None,
):
    """
    Build and save binary classification evaluation reports.

    Args:
        X: Training dataset features pd.DataFrame.
        y: Training dataset target pd.Series.
        pipeline: imbalanced-learn preprocessing pipeline or path to pipeline. Defaults to None.
        threshold: Classification pipeline optimal threshold.
        prefix: Classification reports prefix i.e. pipeline name. Defaults to None.
        destination: Folder where the report should be saved. Defaults to ``METADATA_REGISTRY``.
    """
    # setup
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=cfg.TEST_SIZE, random_state=cfg.RANDOM_STATE
    )

    if not isinstance(pipeline, pp.Pipeline):
        pipeline = joblib.load(pipeline)

    y_proba = pipeline.predict_proba(X_test)

    def predict(x):
        return 1 if x > threshold else 0

    vpredict = np.vectorize(predict)
    vdiscretizer = np.vectorize(discretizer)

    y_pred = vpredict(y_proba[:, 1])
    y_test = vdiscretizer(y_test)

    save_classification_reports(
        y_true=y_test, y_pred=y_pred, prefix=prefix, destination=destination
    )

    save_classification_plots(
        y_true=y_test,
        y_proba=y_proba[:, 1],
        threshold=threshold,
        prefix=prefix,
        destination=destination,
    )

