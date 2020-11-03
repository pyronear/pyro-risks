from pandas import DataFrame

from pyronear_ds.preprocess.geographic_data import GeographicData


class FinalMerger:

    def get_merged_data(
            self, dataclass1: GeographicData, dataclass2: GeographicData
    ) -> DataFrame:
        raise NotImplementedError
