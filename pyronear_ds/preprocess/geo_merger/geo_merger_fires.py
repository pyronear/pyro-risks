import geopandas as gpd

from pyronear_ds.preprocess.geo_merger.geo_merger import GeoMerger
from pyronear_ds.preprocess.geographic_data import GeographicData
from pyronear_ds.preprocess.reader.constants import DEP
from pyronear_ds.preprocess.reader.reader import Reader


class GeoMergerFires(GeoMerger):
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

    def get_merged_data(self) -> GeographicData:
        if self.level != DEP:
            raise NotImplementedError

        data = self.data_reader.read()
        geography = self.geographic_reader.read()
        dict_dep_code_geo = geography.groupby("code")["geometry"].first().to_dict()
        data["DepartementGeometry"] = data["Département"].map(dict_dep_code_geo)
        geo_data = gpd.GeoDataFrame(
            data, geometry="DepartementGeometry", crs="EPSG:4326"
        )
        return GeographicData(geo_data, self.time_col, self.geometry_col)
