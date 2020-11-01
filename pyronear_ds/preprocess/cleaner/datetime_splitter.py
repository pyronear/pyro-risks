import geopandas as gpd

from pyronear_ds.preprocess.cleaner.cleaner import Cleaner


class DatetimeSplitter(Cleaner):
    def clean(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        new_data = data.copy()
        new_data[["Date", "Heure"]] = new_data["Date de première alerte"].str.split(
            " ", expand=True
        )
        return new_data
