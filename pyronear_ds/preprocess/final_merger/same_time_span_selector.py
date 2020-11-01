from typing import Tuple

import geopandas as gpd
import pandas as pd
from pandas import DatetimeIndex


class SameTimeSpanSelector:
    def __init__(self, time_col1: str, time_col2: str):
        self.time_col1 = time_col1
        self.time_col2 = time_col2

    @staticmethod
    def compute_time_span(dataframe: gpd.GeoDataFrame, time_col: str):
        print(dataframe)
        min_time, max_time = dataframe[time_col].min(), dataframe[time_col].max()
        return min_time, max_time

    def find_largest_time_span(
        self, data1: gpd.GeoDataFrame, data2: gpd.GeoDataFrame
    ) -> DatetimeIndex:
        min_time1, max_time1 = self.compute_time_span(data1, self.time_col1)
        time_span1 = pd.date_range(min_time1, max_time1)
        min_time2, max_time2 = self.compute_time_span(data2, self.time_col2)
        time_span2 = pd.date_range(min_time2, max_time2)
        if len(time_span1) > len(time_span2):
            return time_span2
        else:
            return time_span1

    def select_largest_time_span(
        self, data1: gpd.GeoDataFrame, data2: gpd.GeoDataFrame
    ) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        time_span_to_select = self.find_largest_time_span(data1, data2)
        where_time_data1 = data1[self.time_col1].isin(time_span_to_select)
        where_time_data2 = data2[self.time_col2].isin(time_span_to_select)
        return data1[where_time_data1], data2[where_time_data2]
