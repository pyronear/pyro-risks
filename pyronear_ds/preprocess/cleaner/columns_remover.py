from typing import List

import geopandas as gpd

from pyronear_ds.preprocess.cleaner.cleaner import Cleaner


class ColumnsRemover(Cleaner):
    def __init__(self, cols_to_drop: List[str]):
        self.cols_to_drop = cols_to_drop

    def clean(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        data = data.drop(self.cols_to_drop, axis=1)
        return data
