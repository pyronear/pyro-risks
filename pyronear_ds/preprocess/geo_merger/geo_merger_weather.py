import geopandas as gpd

from pyronear_ds.preprocess.geo_merger.geo_merger import GeoMerger
from pyronear_ds.preprocess.reader.constants import DEP
from pyronear_ds.preprocess.reader.reader import Reader


class GeoMergerWeather(GeoMerger):
    def __init__(
        self, data_reader: Reader, geographic_reader: Reader, level: str = DEP
    ):
        self.level = level
        self.data_reader = data_reader
        self.geographic_reader = geographic_reader

    def _get_geodataframe(self) -> gpd.GeoDataFrame:
        data = self.data_reader.read()
        return gpd.GeoDataFrame(
            data,
            geometry=gpd.points_from_xy(data["LONGITUDE"], data["LATITUDE"]),
            crs="EPSG:4326",
        )

    def get_merged_data(self) -> gpd.GeoDataFrame:
        if self.level == DEP:
            return gpd.sjoin(
                self.geographic_reader.read(), self._get_geodataframe(), how="inner"
            )
        else:
            raise NotImplementedError
