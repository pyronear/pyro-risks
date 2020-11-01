import geopandas as gpd


class Cleaner:
    def clean(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        raise NotImplementedError
