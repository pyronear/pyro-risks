import geopandas as gpd

from pyronear_ds.preprocess.cleaner.cleaner import Cleaner


class MissingValuesCleaner(Cleaner):
    def clean(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Remove columns which contains NaN values or
        999/9999 values (equal to missing values according to
        the NOAA documentation).

        :param data: DataFrame object
        :return: DataFrame object
        """
        df_copy = data.copy()
        cols_to_drop = []
        for col in df_copy.columns:
            where_missing = df_copy[col].astype(str).str.contains("999")
            if len(where_missing.value_counts()) > 1:
                cols_to_drop.append(col)
        data = data.drop(cols_to_drop, axis=1)
        return data
