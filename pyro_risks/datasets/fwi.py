# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

import pandas as pd
import numpy as np
from netCDF4 import Dataset
import geopandas as gpd
from typing import Optional, List

import requests
import zipfile
import os
import urllib.request
import json
import logging
import tempfile

from shapely.geometry import Point
from shapely import geometry

from pyro_risks import config as cfg
from pyro_risks.datasets.queries_api import call_fwi
from pyro_risks.datasets.masks import get_french_geom


def load_data(output_path: str) -> None:
    """Load FWI zipped data from github repo and unzip data in folder output_path.

    Args:
        output_path (str): absolute, relative or temporary path
    """
    results = requests.get(cfg.FR_FWI_2019_FALLBACK)

    os.makedirs(output_path, exist_ok=True)
    with open(os.path.join(output_path, "fwi_folder.zip"), "wb") as f:
        f.write(results.content)

    file = zipfile.ZipFile(os.path.join(output_path, "fwi_folder.zip"))
    file.extractall(path=os.path.join(output_path, "fwi_unzipped"))


def include_department(row: pd.Series, polygons_json: json) -> str:
    """Given a row of a dataframe containing longitude and latitude returns name of french department.

    This function makes use of shapely to return if a polygon contains a point.
    Args:
        row (pd.Series): row of dataframe
        polygons_json (json): json with polygons of the departments

    Returns:
        str: name of department or empty string
    """
    for i_dep in range(len(polygons_json["features"])):
        geom = geometry.shape(polygons_json["features"][i_dep]["geometry"])
        if geom.contains(Point((row["longitude"], row["latitude"]))):
            return polygons_json["features"][i_dep]["properties"]["nom"]
    return ""


def get_fwi_from_api(date: str) -> gpd.GeoDataFrame:
    """Call the CDS API and return all fwi variables as a dataframe with geo coordinates and departments.

    When calling the API we get a zip file that must be extracted (in a tmp directory), then handle
    each queried variable which is in a separate netcdf file. A dataframe is created with all the variables
    and then finally we join codes and departments with geopandas.

    Args:
        date (str)

    Returns:
        pd.DataFrame
    """

    year, month, day = date.split("-")
    date_concat = date.replace("-", "")
    with tempfile.TemporaryDirectory() as tmp:
        call_fwi(tmp, year, month, day)

        file = zipfile.ZipFile(os.path.join(tmp, f"fwi_{year}_{month}_{day}.zip"))
        file.extractall(path=os.path.join(tmp, f"fwi_{year}_{month}_{day}"))

        df0 = pd.DataFrame({})
        for var_name in ["BUI", "DC", "DMC", "DSR", "FFMC", "FWI", "ISI"]:
            var_path = os.path.join(
                tmp,
                f"fwi_{year}_{month}_{day}/ECMWF_FWI_{var_name}_{date_concat}_1200_hr_v3.1_int.nc",
            )
            nc = Dataset(var_path, "r")
            lats = nc.variables["latitude"][:]
            var = nc.variables[var_name.lower()][:]
            nc.close()

            lons = np.arange(-180, 180.25, 0.25)
            var_cyclic = np.ma.hstack([var[0][:, 720:], var[0][:, :721]])
            lon2d, lat2d = np.meshgrid(lons, lats)
            df = pd.DataFrame(
                {
                    "latitude": lat2d.flatten(),
                    "longitude": lon2d.flatten(),
                    var_name.lower(): var_cyclic.flatten(),
                }
            )
            df = df.dropna(subset=[var_name.lower()])
            df = df.reset_index(drop=True)
            if var_name == "BUI":
                df0 = pd.concat([df0, df], axis=1)
            else:
                df0 = pd.merge(df0, df, on=["latitude", "longitude"], how="inner")
    geo_data = gpd.GeoDataFrame(
        df0,
        geometry=gpd.points_from_xy(df0["longitude"], df0["latitude"]),
        crs="EPSG:4326",
    )
    geo_masks = get_french_geom()
    geo_masks[["lon_1", "lat_1", "lon_2", "lat_2"]] = geo_masks["geometry"].bounds
    min_lon = min(geo_masks.lon_1.min(), geo_masks.lon_2.min())
    max_lon = max(geo_masks.lon_1.max(), geo_masks.lon_2.max())
    min_lat = min(geo_masks.lat_1.min(), geo_masks.lat_2.min())
    max_lat = max(geo_masks.lat_1.max(), geo_masks.lat_2.max())
    geo_masks = geo_masks.drop(columns=["lon_1", "lat_1", "lon_2", "lat_2"])
    geo_data = geo_data.loc[
        (geo_data.latitude >= min_lat)
        & (geo_data.latitude <= max_lat)
        & (geo_data.longitude >= min_lon)
        & (geo_data.longitude <= max_lon)
    ]
    geo_df = gpd.sjoin(geo_masks, geo_data, how="inner")
    return geo_df.drop(["index_right", "geometry"], axis=1)


def get_fwi_data_for_predict(date: str) -> pd.DataFrame:
    """Run CDS API queries for dates required by the model and return fwi dataset for predict step.

    This takes care principally of the lags required for the modelling step.

    Args:
        date (str)

    Returns:
        pd.DataFrame
    """
    data = get_fwi_from_api(date)
    data["day"] = date
    # Lag J-1
    lag = np.datetime64(date) - np.timedelta64(1, "D")
    dataJ1 = get_fwi_from_api(str(lag))
    dataJ1["day"] = str(lag)
    # Lag J-3
    lag = np.datetime64(date) - np.timedelta64(3, "D")
    dataJ3 = get_fwi_from_api(str(lag))
    dataJ3["day"] = str(lag)
    # Lag J-7
    lag = np.datetime64(date) - np.timedelta64(7, "D")
    dataJ7 = get_fwi_from_api(str(lag))
    dataJ7["day"] = str(lag)
    merged_data = pd.concat([data, dataJ1, dataJ3, dataJ7], ignore_index=True)
    return merged_data


def get_fwi_data(source_path: str, day: Optional[str] = "20190101") -> pd.DataFrame:
    """Load and handle netcdf data for selected day.

    Return pandas dataframe with longitude, latitude, day and fwi indices
    (fwi, ffmc, dmc, dc, isi, bui, dsr, dr).
    Args:
        source_path (str): path with unzipped netcdf fwi data, usually got from load_data.
        day (str, optional): which day to load. Defaults to '20190101'.

    Returns:
        pd.DataFrame: dataframe with all fwi indices for selected day
    """
    nc = Dataset(
        os.path.join(source_path, "fwi_unzipped/JRC_FWI_{}.nc".format(day)), "r"
    )
    try:
        lons = nc.variables["lon"][:]
        lats = nc.variables["lat"][:]
        fwi = nc.variables["fwi"][:]
        ffmc = nc.variables["ffmc"][:]
        dmc = nc.variables["dmc"][:]
        dc = nc.variables["dc"][:]
        isi = nc.variables["isi"][:]
        bui = nc.variables["bui"][:]
        dsr = nc.variables["dsr"][:]
        dr = nc.variables["danger_risk"][:]
    except KeyError:
        print("Some reading error with: ", day)
    nc.close()

    lon2d, lat2d = np.meshgrid(lons, lats)

    df = pd.DataFrame(
        {
            "latitude": lat2d.flatten(),
            "longitude": lon2d.flatten(),
            "day": day,
            "fwi": fwi[0, :, :].flatten(),
            "ffmc": ffmc[0, :, :].flatten(),
            "dmc": dmc[0, :, :].flatten(),
            "dc": dc[0, :, :].flatten(),
            "isi": isi[0, :, :].flatten(),
            "bui": bui[0, :, :].flatten(),
            "dsr": dsr[0, :, :].flatten(),
            "dr": dr[0, :, :].flatten(),
        }
    )
    df = df.dropna(subset=["fwi", "ffmc", "dmc", "dc", "isi", "bui", "dsr", "dr"])
    df = df.reset_index(drop=True)
    return df


def create_departement_df(day_data: pd.DataFrame) -> pd.DataFrame:
    """Create dataframe with lon, lat coordinates and corresponding departments.

    Load json with the department polygons and run function include_department to get the
    name of departments corresponding to each row of input data, typically one day of FWI data
    got with load_data. This may take a few minutes due to the shapely process.
    Args:
        day_data (pd.Dataframe): df with longitudes and latitudes

    Returns:
        pd.DataFrame: dataframe with lat, lon and department
    """
    df = day_data.copy()

    with urllib.request.urlopen(cfg.FR_GEOJSON) as url:
        dep_polygons = json.loads(url.read().decode())

    deps = [include_department(df.iloc[i], dep_polygons) for i in range(df.shape[0])]
    df["departement"] = deps
    df = df[df["departement"] != ""]
    dep_geo_df = df[["latitude", "longitude", "departement"]]
    return dep_geo_df


class GwisFwi(pd.DataFrame):
    """GWIS FWI dataframe (8 km resolution) on French territory based on 2019-2020 data."""

    def __init__(self, days_list: List[str] = ["20190101"]) -> None:
        """Create dataframe with fwi indices data corresponding to days_list and join french department.

        Args:
            days_list: list of str, format year month day (all concatenated)
        """
        fwi_df = pd.DataFrame(
            columns=[
                "latitude",
                "longitude",
                "day",
                "fwi",
                "ffmc",
                "dmc",
                "dc",
                "isi",
                "bui",
                "dsr",
                "dr",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            load_data(output_path=tmp)
            for day in days_list:
                df = get_fwi_data(source_path=tmp, day=day)
                fwi_df = pd.concat([fwi_df, df])
            dep_geo_df = create_departement_df(df)
            fwi_df = pd.merge(fwi_df, dep_geo_df, on=["latitude", "longitude"])
        super().__init__(fwi_df)
