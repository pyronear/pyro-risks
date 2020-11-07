import logging
import pandas as pd
import geopandas as gpd
from typing import List, Optional

from pyronear_ds import config as cfg
from .masks import get_french_geom

__all__ = ['NOAAWeather']


class NOAAWeather(pd.DataFrame):
    """Weather dataset on French territory, accessible upon request to NOAA. Requests are to be made at:
    https://www.ncdc.noaa.gov/cdo-web.

    Args:
        source_path: path or URL to your version of the source data
        use_cols: columns to read from source
    """

    kept_cols = ['DATE', 'LATITUDE', 'LONGITUDE', 'ELEVATION', 'DEWP', 'DEWP_ATTRIBUTES',
                 'FRSHTT', 'GUST', 'MAX', 'MIN', 'MXSPD', 'PRCP', 'SLP', 'SLP_ATTRIBUTES',
                 'SNDP', 'STP', 'STP_ATTRIBUTES', 'TEMP', 'TEMP_ATTRIBUTES',
                 'VISIB', 'VISIB_ATTRIBUTES', 'WDSP', 'WDSP_ATTRIBUTES']

    def __init__(self, source_path: Optional[str] = None, use_cols: Optional[List[str]] = None) -> None:
        if not isinstance(source_path, str):
            # Download in cache
            logging.warning(f"No data source specified for {self.__class__.__name__}, trying fallback.")
            source_path = cfg.FR_WEATHER_FALLBACK
        if not isinstance(use_cols, list):
            use_cols = self.kept_cols
        data = pd.read_csv(source_path, usecols=use_cols)
        geo_df = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data["LONGITUDE"], data["LATITUDE"]),
                                  crs="EPSG:4326")
        # Match the polygons using the ones of each predefined country area
        geo_masks = get_french_geom()
        geo_data = gpd.sjoin(geo_masks, geo_df, how="inner")
        # Drop NA
        geo_data = geo_data.dropna(axis=1)
        # Convert
        geo_data['DATE'] = pd.to_datetime(geo_data['DATE'], format="%Y-%m-%d", errors='coerce')
        # Drop Cols
        super().__init__(geo_data.drop(['index_right', 'geometry'], axis=1))
