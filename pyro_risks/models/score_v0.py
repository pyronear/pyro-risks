from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import precision_recall_curve
import xgboost as xgb
import pandas as pd
import numpy as np


__all__ = [
    "prepare_dataset",
    "target_correlated_features",
    "split_train_test",
    "add_lags",
    "train_random_forest",
    "xgb_model",
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


RF_PARAMS = {
    "n_estimators": 500,
    "min_samples_leaf": 10,
    "max_features": "sqrt",
    "class_weight": "balanced",
    "criterion": "gini",
    "random_state": 10,
    "n_jobs": -1,
}

XGB_PARAMS = {
    "max_depth": 10,
    "min_child_weight": 10,
    "eta": 0.01,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "binary:logistic",
    "eval_metric": ["logloss", "aucpr"],
}


def prepare_dataset(df, selected_dep=SELECTED_DEP):
    """Filter departments, create target and filter correlated features to target.

    Args:
        df (pd.DataFrame): dataframe containing at least day, department and fires columns
        selected_dep (list, optional): departments to consider. Defaults to SELECTED_DEP.

    Returns:
        tuple: X pd.DataFrame, y pd.Series
    """
    df = df[df["departement"].isin(selected_dep)].copy()
    df = df.fillna(-1)

    y = df["fires"] > 0
    y = y.astype(int)
    y.name = "classif_target"

    selected_feat = target_correlated_features(
        df.drop(["day", "departement", "fires"], axis=1), y
    )
    X = df[selected_feat]
    return X, y


def target_correlated_features(X, y, threshold=0.15):
    """Return features of X correlated to y according to a given threshold.

    Args:
        X (pd.DataFrame): df with several features
        y (pd.Series): binary target

    Returns:
        list of str: features mostly correlated to target
    """
    corr_to_target = (
        pd.concat([X, y], axis=1)
        .corr(method="pearson")
        .loc[y.name]
        .apply(abs)
        .sort_values(ascending=False)
    )
    corr_to_target = corr_to_target[corr_to_target.index != y.name]
    selected_feat = corr_to_target[corr_to_target > threshold].index.tolist()
    return selected_feat


def split_train_test(X, y):
    """Train test split (sklearn) with fixed test size and random state."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test


def add_lags(df, cols):
    """Add lags to dataframe df of the selected columns.

    Lags added correspond to day -1, -3 and -7 and are added to each department separately.

    Args:
        df (pd.DataFrame): main dataframe with departement and day columns
        cols (list of str): columns on which to add lags

    Returns:
        [type]: [description]
    """
    for var in cols:
        for dep in df["departement"].unique():
            tmp = df[df["departement"] == dep][["day", var]].set_index("day")
            tmp1 = tmp.copy()
            tmp1 = tmp1.join(
                tmp.shift(periods=1, freq="D"), rsuffix="_lag1", how="left"
            )
            tmp1 = tmp1.join(
                tmp.shift(periods=3, freq="D"), rsuffix="_lag3", how="left"
            )
            tmp1 = tmp1.join(
                tmp.shift(periods=7, freq="D"), rsuffix="_lag7", how="left"
            )
            new_vars = [var + "_lag1", var + "_lag3", var + "_lag7"]
            df.loc[df["departement"] == dep, new_vars] = tmp1[new_vars].values
    return df


def train_random_forest(
    X_train, X_test, y_train, y_test, params=RF_PARAMS, ignore_prints=True
):
    """Train a random forest classifier on split train/test, get predictions and associated metrics.

    Print classification reports on train and test set as well as best threshold and best F1-score.
    Args:
        X_train (pd.DataFrame): train set
        X_test (pd.DataFrame): test set
        y_train (pd.Series): binary train target
        y_test (pd.Series): binary test target
        params (dict, optional): random forest hyperparams. Defaults to RF_PARAMS
        ignore_prints (bool, optional): whether to print results

    Returns:
        sklearn model: fitted random forest classifier
    """
    rfc = RandomForestClassifier(**params)
    rfc.fit(X_train, y_train)

    train_preds = rfc.predict(X_train)
    preds = rfc.predict(X_test)

    if not ignore_prints:
        print("On Train Set")
        print(classification_report(y_train, train_preds))
        print("On Test Set")
        print(classification_report(y_test, preds))

    y_score = rfc.predict_proba(X_test)
    prec, recall, thresholds = precision_recall_curve(y_test, y_score[:, 1])
    fscore = (2 * prec * recall) / (prec + recall)
    ix = np.argmax(fscore)
    if not ignore_prints:
        print("Best Threshold=%f, F-Score=%.3f" % (thresholds[ix], fscore[ix]))
    return rfc


def xgb_model(
    X_train,
    y_train,
    X_test,
    y_test,
    params=XGB_PARAMS,
    num_round=1000,
    ignore_prints=True,
):
    """Train a xgboost classifier on split train/test, get predictions and associated metrics.

    Args:
        X_train (pd.DataFrame): train set
        X_test (pd.DataFrame): test set
        y_train (pd.Series): binary train target
        y_test (pd.Series): binary test target
        params (dict, optional): xgboost hyperparams. Defaults to XGB_PARAMS
        num_round (int, optional): boosting rounds. Defaults to 1000
        ignore_prints (bool, optional): whether to print results

    Returns:
        xgboost model, progress on train and validation, and predictions
    """

    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    progress = dict()

    model = xgb.train(
        params=params,
        dtrain=dtrain,
        num_boost_round=num_round,
        evals=[(dtrain, "Train"), (dtest, "Test")],
        evals_result=progress,
        early_stopping_rounds=50,
        verbose_eval=False,
    )
    preds = model.predict(dtest)
    if not ignore_prints:
        print(
            "Best AUCPR Test score: {:.2f} with {} rounds".format(
                model.best_score, model.best_iteration + 1
            )
        )

    y_score = preds

    prec, recall, thresholds = precision_recall_curve(y_test, y_score)
    fscore = (2 * prec * recall) / (prec + recall)
    ix = np.argmax(fscore)
    if not ignore_prints:
        print("Best Threshold=%f, F-Score=%.3f" % (thresholds[ix], fscore[ix]))

    return model, progress, preds
