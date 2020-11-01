import geopandas as gpd
import pandas as pd
from pandas import DataFrame


class FinalMerger:
    def __init__(
        self,
        time_col1: str,
        time_col2: str,
        geometry_col1: str,
        geometry_col2: str,
        how: str,
    ):
        self.time_col1 = time_col1
        self.time_col2 = time_col2
        self.geometry_col1 = geometry_col1
        self.geometry_col2 = geometry_col2
        self.how = how

    def get_merged_data(
        self, data1: gpd.GeoDataFrame, data2: gpd.GeoDataFrame
    ) -> DataFrame:
        final_data = pd.merge(
            data1,
            data2,
            left_on=[self.time_col1, self.geometry_col1],
            right_on=[self.time_col2, self.geometry_col2],
            how=self.how,
        )
        return final_data
