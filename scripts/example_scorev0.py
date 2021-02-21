# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from pyro_risks.datasets import MergedEraFwiViirs
from pyro_risks.models.score_v0 import (
    add_lags,
    prepare_dataset,
    train_random_forest,
    split_train_test,
    xgb_model,
)

SELECTED_DEP = [
    "Pyrénées-Atlantiques",
    "Hautes-Pyrénées",
    "Ariège",
    "Haute-Corse",
    "Lozère",
    "Gard",
    "Hérault",
    "Bouches-du-Rhônes",
    "Pyrénées-Orientales",
    "Cantal",
    "Alpes-Maritimes",
    "Aveyron",
]


def run():
    df = MergedEraFwiViirs()
    df_lags = add_lags(df, df.drop(["day", "departement", "fires"], axis=1).columns)
    X, y = prepare_dataset(df_lags, selected_dep=SELECTED_DEP)
    X_train, X_test, y_train, y_test = split_train_test(X, y)
    train_random_forest(X_train, X_test, y_train, y_test, ignore_prints=False)
    xgb_model(X_train, y_train, X_test, y_test, ignore_prints=False)


if __name__ == "__main__":
    run()
