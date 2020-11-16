import logging
from typing import Optional

import geopandas as gpd
import pandas as pd
import requests
import xarray as xr

from pyro_risks import config as cfg
from .masks import get_french_geom

__all__ = ["ERA5Land"]


class ERA5Land(pd.DataFrame):
    """Provides ERA5-Land clean dataset as a pandas dataframe.

    ERA5-Land is a reanalysis dataset providing a consistent view of the evolution of land variables
    over several decades at an enhanced resolution compared to ERA5. ERA5-Land uses as input to
    control the simulated land fields ERA5 atmospheric variables, such as air temperature and air humidity.
    Using cdaspi https://pypi.org/project/cdsapi/ with access key, the user can get the dataset
    at https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=overview

    The provided dataset has to be in netCDF4 format here.

    Args:
        source_path: str
            Path or URL to your version of the source data
    """

    def __init__(self, source_path: Optional[str] = None):
        """
        Args:
            source_path: Optional[str]
                Path or URL to your version of the source data
        """
        if not isinstance(source_path, str):
            # Download in cache
            logging.warning(
                f"No data source specified for {self.__class__.__name__}, trying fallback."
            )
            source_path = cfg.FR_ERA5LAND_FALLBACK

        with requests.get(source_path) as resp:
            ds = xr.open_dataset(resp.content)
            data = ds.to_dataframe()

        # Drop NaNs which correspond to no land
        data = data.dropna()
        data = data.reset_index()

        data["time"] = pd.to_datetime(
            data["time"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
        )
        data["time"] = data["time"].dt.normalize()

        # Transform into geopandas dataframe
        geo_data = gpd.GeoDataFrame(
            data,
            geometry=gpd.points_from_xy(data["longitude"], data["latitude"]),
            crs="EPSG:4326",
        )

        # Match the polygons using the ones of each predefined country area
        geo_masks = get_french_geom()
        geo_df = gpd.sjoin(geo_masks, geo_data, how="inner")
        super().__init__(geo_df.drop(["index_right", "geometry"], axis=1))
