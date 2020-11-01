import geopandas as gpd

from pyronear_ds.preprocess.reader.constants import DEP
from pyronear_ds.preprocess.reader.reader import Reader


class GeographicReader(Reader):
    def __init__(self, url: str, level: str = DEP):
        self.url = url
        self.level = level

    def read(self) -> gpd.GeoDataFrame:
        if self.level == DEP:
            return gpd.read_file(self.url)
        else:
            raise NotImplementedError
