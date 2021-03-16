# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from pyro_risks.datasets.utils import download
from datetime import datetime
from typing import Tuple

import pyro_risks.config as cfg
import pandas as pd
import os

__all__ = ["load_dataset"]


def load_dataset() -> Tuple[pd.DataFrame, pd.Series]:
    """
    Load Pyro Risks training datasets.

    Download and load Pyro Risks training datasets.

    Returns:
        Tuple[pd.DataFrame, pd.Series]: [description]
    """
    dataset_path = os.path.join(cfg.DATA_REGISTRY, cfg.DATASET)
    usecols = [cfg.DATE_VAR, cfg.ZONE_VAR, cfg.TARGET] + cfg.PIPELINE_ERA5T_VARS
    pipeline_vars = [cfg.DATE_VAR, cfg.ZONE_VAR] + cfg.PIPELINE_ERA5T_VARS

    if not os.path.isfile(dataset_path):
        download(
            url=cfg.ERA5T_VIIRS_PIPELINE,
            default_extension="csv",
            unzip=False,
            destination=cfg.DATA_REGISTRY,
        )

    df = pd.read_csv(dataset_path, usecols=usecols)
    df["day"] = df["day"].apply(
        lambda x: datetime.strptime(str(x), "%Y-%m-%d") if not pd.isnull(x) else x
    )

    X = df[pipeline_vars]
    y = df[cfg.TARGET]
    return X, y
