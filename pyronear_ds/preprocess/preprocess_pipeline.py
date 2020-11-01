from typing import List

from pyronear_ds.preprocess.cleaner.cleaner import Cleaner
from pyronear_ds.preprocess.data_provider.data_provider import DataProvider
from pyronear_ds.preprocess.final_merger.final_merger import FinalMerger
from pyronear_ds.preprocess.final_merger.same_time_span_selector import (
    SameTimeSpanSelector,
)


class PreprocessPipeline:
    def __init__(
        self,
        data_provider1: DataProvider,
        data_provider2: DataProvider,
        time_span_selector: SameTimeSpanSelector,
        final_merger: FinalMerger,
        cleaners: List[Cleaner],
    ):
        self.data_provider1 = data_provider1
        self.data_provider2 = data_provider2
        self.time_span_selector = time_span_selector
        self.final_merger = final_merger
        self.cleaners = cleaners

    def pipeline(self):
        data1 = self.data_provider1.get_cleaned_data()
        data2 = self.data_provider2.get_cleaned_data()
        data1, data2 = self.time_span_selector.select_largest_time_span(data1, data2)
        merged_data = self.final_merger.get_merged_data(data1, data2)
        for cleaner in self.cleaners:
            merged_data = cleaner.clean(merged_data)
        return merged_data
