from typing import List

from pyronear_ds.preprocess.cleaner.cleaner import Cleaner
from pyronear_ds.preprocess.geo_merger.geo_merger import GeoMerger
from pyronear_ds.preprocess.geographic_data import GeographicData


class DataProvider:
    def __init__(self, raw_data_provider: GeoMerger, raw_data_cleaners: List[Cleaner]):
        self.raw_data_provider = raw_data_provider
        self.raw_data_cleaners = raw_data_cleaners

    def get_cleaned_data(self) -> GeographicData:
        geographic_data_instance = self.raw_data_provider.get_merged_data()
        for cleaner in self.raw_data_cleaners:
            geographic_data_instance.dataframe = cleaner.clean(
                geographic_data_instance.dataframe
            )
        return geographic_data_instance
