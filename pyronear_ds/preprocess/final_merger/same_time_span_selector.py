from typing import Tuple

import pandas as pd
from pandas import DatetimeIndex, DataFrame

from pyronear_ds.preprocess.geographic_data import GeographicData


class SameTimeSpanSelector:
    @staticmethod
    def compute_time_span(dataframe: DataFrame, time_col: str):
        min_time, max_time = dataframe[time_col].min(), dataframe[time_col].max()
        return min_time, max_time

    def find_smallest_time_span(
            self, dataclass1: GeographicData, dataclass2: GeographicData
    ) -> DatetimeIndex:
        min_time1, max_time1 = self.compute_time_span(
            dataclass1.dataframe, dataclass1.time_col
        )
        time_span1 = pd.date_range(min_time1, max_time1)
        min_time2, max_time2 = self.compute_time_span(
            dataclass2.dataframe, dataclass2.time_col
        )
        time_span2 = pd.date_range(min_time2, max_time2)
        if len(time_span1) > len(time_span2):
            return time_span2
        else:
            return time_span1

    def select_smallest_time_span(
            self, dataclass1: GeographicData, dataclass2: GeographicData
    ) -> Tuple[GeographicData, GeographicData]:
        time_span_to_select = self.find_smallest_time_span(dataclass1, dataclass2)
        where_time_data1 = dataclass1.dataframe[dataclass1.time_col].isin(
            time_span_to_select
        )
        where_time_data2 = dataclass2.dataframe[dataclass2.time_col].isin(
            time_span_to_select
        )
        dataclass1.dataframe = dataclass1.dataframe[where_time_data1]
        dataclass2.dataframe = dataclass2.dataframe[where_time_data2]
        return (
            dataclass1,
            dataclass2,
        )
