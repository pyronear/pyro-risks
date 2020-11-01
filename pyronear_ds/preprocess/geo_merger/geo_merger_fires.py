import geopandas as gpd

from pyronear_ds.preprocess.geo_merger.geo_merger import GeoMerger
from pyronear_ds.preprocess.reader.constants import DEP
from pyronear_ds.preprocess.reader.reader import Reader


class GeoMergerFires(GeoMerger):
    def __init__(
        self, data_reader: Reader, geographic_reader: Reader, level: str = DEP
    ):
        self.level = level
        self.data_reader = data_reader
        self.geographic_reader = geographic_reader

    def get_merged_data(self) -> gpd.GeoDataFrame:
        if self.level != DEP:
            raise NotImplementedError

        data = self.data_reader.read()
        geography = self.geographic_reader.read()
        dict_dep_code_geo = geography.groupby("code")["geometry"].first().to_dict()
        data["DepartementGeometry"] = data["Département"].map(dict_dep_code_geo)
        return gpd.GeoDataFrame(data, geometry="DepartementGeometry", crs="EPSG:4326")
