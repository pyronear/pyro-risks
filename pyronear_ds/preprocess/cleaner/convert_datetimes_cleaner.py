from typing import Dict

import geopandas as gpd
import pandas as pd

from pyronear_ds.preprocess.cleaner.cleaner import Cleaner


class ConvertDatetimesCleaner(Cleaner):
    def __init__(self, formats: Dict[str, str]):
        self.formats = formats

    def clean(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Convert string columns denoting datetimes to datetimes with a specified format.

        :param:
        formats: Dict[str, str]
            Dict of datetime formats, with column names as keys and datetime formats as values.
        """
        for col, fmt in self.formats.items():
            data[col] = data[col].astype(str)
            data[col] = pd.to_datetime(data[col], format=fmt, errors="coerce")
        return data
