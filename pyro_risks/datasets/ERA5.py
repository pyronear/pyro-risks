import logging
from typing import Optional

import os
import geopandas as gpd
import pandas as pd
import numpy as np
import requests
import xarray as xr
import tempfile

from pyro_risks import config as cfg
from .masks import get_french_geom
from pyro_risks.datasets.queries_api import call_era5land, call_era5t


__all__ = ["ERA5Land", "ERA5T"]


def get_data_era5land_for_predict(date: str) -> pd.DataFrame:
    """
    Get ERA5Land dataframe for given date using call to cdsapi
    and appropriate class.
​
    Args:
        date: str
    Date with the following format: "YEAR-MONTH-DAY" eg. "2020-05-12"
​
    Returns: pd.DataFrame
        Dataframe containing ERA5 Land data for the requested day.
    """
    with tempfile.TemporaryDirectory() as tmp:
        year, month, day = date.split("-")
        call_era5land(tmp, year, month, day)
        # TODO: make sure that the directory works when on server
        data = ERA5Land(source_path=os.path.join(cfg.CACHE_FOLDER, f"era5land_{year}_{month}_{day}.nc"))

        # Lag J-1
        lag = np.datetime64(date) - np.timedelta64(1, "D")
        year, month, day = str(lag).split("-")
        call_era5land(tmp, year, month, day)
        dataJ1 = ERA5Land(source_path=os.path.join(cfg.CACHE_FOLDER, f"era5land_{year}_{month}_{day}.nc"))

        # Lag J-3
        lag = np.datetime64(date) - np.timedelta64(3, "D")
        year, month, day = str(lag).split("-")
        call_era5land(tmp, year, month, day)
        dataJ3 = ERA5Land(source_path=os.path.join(cfg.CACHE_FOLDER, f"era5land_{year}_{month}_{day}.nc"))

        # Lag J-7
        lag = np.datetime64(date) - np.timedelta64(7, "D")
        year, month, day = str(lag).split("-")
        call_era5land(tmp, year, month, day)
        dataJ7 = ERA5Land(source_path=os.path.join(cfg.CACHE_FOLDER, f"era5land_{year}_{month}_{day}.nc"))

        merged_data = pd.concat([data, dataJ1, dataJ3, dataJ7], ignore_index=True)
        return merged_data


def get_data_era5t_for_predict(date: str) -> pd.DataFrame:
    """
    Get ERA5T dataframe for given date using call to cdsapi
    and appropriate class.
​
    Args:
        date: str
    Date with the following format: "YEAR-MONTH-DAY" eg. "2020-05-12"
​
    Returns: pd.DataFrame
        Dataframe containing ERA5T data for the requested day.
    """
    with tempfile.TemporaryDirectory() as tmp:
        year, month, day = date.split("-")
        call_era5t(tmp, year, month, day)
        # TODO: make sure that the directory works when on server
        data = ERA5T(source_path=os.path.join(tmp, f"era5t_{year}_{month}_{day}.nc"))
        # Lag J-1
        lag = np.datetime64(f"{year}-{month}-{day}") - np.timedelta64(1, "D")
        year, month, day = str(lag).split("-")
        call_era5t(tmp, year, month, day)
        dataJ1 = ERA5T(source_path=os.path.join(tmp, f"era5t_{year}_{month}_{day}.nc"))
        # Lag J-3
        lag = np.datetime64(f"{year}-{month}-{day}") - np.timedelta64(3, "D")
        year, month, day = str(lag).split("-")
        call_era5t(tmp, year, month, day)
        dataJ3 = ERA5T(source_path=os.path.join(tmp, f"era5t_{year}_{month}_{day}.nc"))
        # Lag J-7
        lag = np.datetime64(f"{year}-{month}-{day}") - np.timedelta64(7, "D")
        year, month, day = str(lag).split("-")
        call_era5t(tmp, year, month, day)
        dataJ7 = ERA5T(source_path=os.path.join(tmp, f"era5t_{year}_{month}_{day}.nc"))
        merged_data = pd.concat([data, dataJ1, dataJ3, dataJ7], ignore_index=True)
        return merged_data


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

        if source_path.startswith("http"):
            with requests.get(source_path) as resp:
                ds = xr.open_dataset(resp.content)
                data = ds.to_dataframe()
        else:
            ds = xr.open_dataset(source_path)
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


class ERA5T(pd.DataFrame):
    """Provides ERA5T clean dataset as a pandas dataframe.

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
            source_path = cfg.FR_ERA5T_FALLBACK

        if source_path.startswith("http"):
            with requests.get(source_path) as resp:
                ds = xr.open_dataset(resp.content)
                data = ds.to_dataframe()
        else:
            ds = xr.open_dataset(source_path)
            data = ds.to_dataframe()

        # Drop columns with NaNs
        data = data.dropna(axis=1)
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
