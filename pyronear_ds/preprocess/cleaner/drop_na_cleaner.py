from typing import List

import geopandas as gpd

from pyronear_ds.preprocess.cleaner.cleaner import Cleaner


class DropNaCleaner(Cleaner):
    def __init__(self, cols_to_except: List[str] = None):
        self.cols_to_except = cols_to_except or []

    def clean(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        data_tmp = data.dropna(axis=1)
        cols_to_keep = data_tmp.columns.tolist()
        cols_to_keep += self.cols_to_except
        return data[cols_to_keep]
