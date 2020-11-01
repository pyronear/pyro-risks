from typing import List

import geopandas as gpd

from pyronear_ds.preprocess.cleaner.cleaner import Cleaner
from pyronear_ds.preprocess.geo_merger.geo_merger import GeoMerger


class DataProvider:
    def __init__(self, raw_data_provider: GeoMerger, raw_data_cleaners: List[Cleaner]):
        self.raw_data_provider = raw_data_provider
        self.raw_data_cleaners = raw_data_cleaners

    def get_cleaned_data(self) -> gpd.GeoDataFrame:
        data = self.raw_data_provider.get_merged_data().dataframe
        for cleaner in self.raw_data_cleaners:
            data = cleaner.clean(data)
        return data
