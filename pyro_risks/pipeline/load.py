# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import Optional, List
from pyro_risks.datasets.utils import download
from datetime import datetime
from typing import Tuple

import pyro_risks.config as cfg
import pandas as pd
import os

__all__ = ["load_dataset"]


def load_dataset(
    url: Optional[str] = None,
    path: Optional[str] = None,
    usecols: Optional[List[str]] = None,
    pipeline_cols: Optional[List[str]] = None,
    destination: str = None,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Load Pyro Risks training datasets.

    Download and load Pyro Risks training datasets.

    Args:
        url: Training dataset URL. Defaults to None.
        path: Dataset full path. Defaults to None.
        usecols: Subset of the dataset columns. Defaults to None.
        pipeline_cols: Subset of the dataset used for training. Defaults to None.
        destination: folder where the dataset should be saved. Defaults to None.

    Returns:
        Tuple[pd.DataFrame, pd.Series]
    """
    url = cfg.ERA5T_VIIRS_PIPELINE if url is None else url
    path = os.path.join(cfg.DATA_REGISTRY, cfg.DATASET) if path is None else path
    usecols = (
        [cfg.DATE_VAR, cfg.ZONE_VAR, cfg.TARGET] + cfg.PIPELINE_ERA5T_VARS
        if usecols is None
        else usecols
    )
    pipeline_cols = (
        [cfg.DATE_VAR, cfg.ZONE_VAR] + cfg.PIPELINE_ERA5T_VARS
        if pipeline_cols is None
        else pipeline_cols
    )
    destination = cfg.DATA_REGISTRY if destination is None else destination

    if not os.path.isfile(path):
        download(url=url, default_extension="csv", unzip=False, destination=destination)

    df = pd.read_csv(path, usecols=usecols)
    df["day"] = df["day"].apply(
        lambda x: datetime.strptime(str(x), "%Y-%m-%d") if not pd.isnull(x) else x
    )

    X = df[pipeline_cols]
    y = df[cfg.TARGET]
    return X, y
