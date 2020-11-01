import geopandas as gpd

from pyronear_ds.preprocess.geo_merger.geo_merger import GeoMerger
from pyronear_ds.preprocess.geographic_data import GeographicData
from pyronear_ds.preprocess.reader.constants import DEP
from pyronear_ds.preprocess.reader.reader import Reader


class GeoMergerWeather(GeoMerger):
    def __init__(
        self,
        data_reader: Reader,
        geographic_reader: Reader,
        time_col: str,
        geometry_col: str,
        level: str = DEP,
    ):
        self.data_reader = data_reader
        self.geographic_reader = geographic_reader
        self.time_col = time_col
        self.geometry_col = geometry_col
        self.level = level

    def _get_geodataframe(self) -> gpd.GeoDataFrame:
        data = self.data_reader.read()
        return gpd.GeoDataFrame(
            data,
            geometry=gpd.points_from_xy(data["LONGITUDE"], data["LATITUDE"]),
            crs="EPSG:4326",
        )

    def get_merged_data(self) -> GeographicData:
        if self.level == DEP:
            geo_data = gpd.sjoin(
                self.geographic_reader.read(), self._get_geodataframe(), how="inner"
            )
            return GeographicData(geo_data, self.time_col, self.geometry_col)
        else:
            raise NotImplementedError
