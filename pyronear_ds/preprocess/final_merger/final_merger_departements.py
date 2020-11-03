import pandas as pd
from pandas import DataFrame

from pyronear_ds.preprocess.final_merger.final_merger import FinalMerger
from pyronear_ds.preprocess.geographic_data import GeographicData


class FinalMergerDepartement(FinalMerger):
    def __init__(
            self, how: str,
    ):
        self.how = how

    def get_merged_data(
            self, dataclass1: GeographicData, dataclass2: GeographicData
    ) -> DataFrame:
        final_data = pd.merge(
            dataclass1.dataframe,
            dataclass2.dataframe,
            left_on=[dataclass1.time_col, dataclass1.geometry_col],
            right_on=[dataclass2.time_col, dataclass2.geometry_col],
            how=self.how,
        )
        return final_data
