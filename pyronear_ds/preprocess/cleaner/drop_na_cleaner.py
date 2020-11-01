from typing import List

import geopandas as gpd

from pyronear_ds.preprocess.cleaner.cleaner import Cleaner


class DropNaCleaner(Cleaner):
    def clean(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        return data.dropna(axis=1)

    # TODO: fix cleaner for fire dataset
