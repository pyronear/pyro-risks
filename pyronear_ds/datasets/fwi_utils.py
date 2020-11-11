import requests
import zipfile
import os
import urllib.request
import json

import pandas as pd
import numpy as np
from netCDF4 import Dataset

from shapely.geometry import Point
from shapely import geometry
from shapely.geometry.polygon import Polygon

from pyronear_ds import config as cfg


def load_data(source_path=None, output_path=cfg.DATA_PATH):
    """Load FWI zipped data from github repo and unzip data in folder output_path
    """
    if not isinstance(source_path, str):
        source_path = cfg.FR_FWI_2019_FALLBACK
    results = requests.get(source_path)

    os.makedirs(output_path, exist_ok=True)
    with open(output_path + 'fwi_folder.zip', 'wb') as f:
        f.write(results.content)

    file = zipfile.ZipFile(output_path + 'fwi_folder.zip')
    file.extractall(path=output_path + 'fwi_unzipped')


def include_department(row, polygons_json):
    """Given a row of a dataframe containing longitude and latitude returns name of french department.
    This function makes use of shapely to return if a polygon contains a point.

    Args:
        row (pd.Series): row of dataframe
        polygons_json (json): json with polygons of the departments

    Returns:
        str: name of department or empty string
    """
    for i_dep in range(len(polygons_json['features'])):
        geom = geometry.shape(polygons_json['features'][i_dep]['geometry'])
        if geom.contains(Point((row['longitude'], row['latitude']))):
            return polygons_json['features'][i_dep]['properties']['nom']
    return ""


def create_departement_df(source_path=cfg.DATA_PATH, day='20190101'):
    """Create dataframe with lon, lat coordinates and corresponding departments.

    To do this we load one netcdf with FWI data, drop NaN (no land), load the json with the
    department polygons and run function include_department to get the name of departments.
    Save in source_path dataframe with lat, lon points having non-empty departments.

    This may take a few minutes.

    Args:
        source_path (str, optional): where to find the netcdf from the load_data step.
            Defaults to config.DATA_PATH.
        day (str, optional): which netcdf to load to make the dataframe. Defaults to '20190101'.
    """

    nc = Dataset(source_path + 'fwi_unzipped/JRC_FWI_{}.nc'.format(day), 'r')
    lons = nc.variables['lon'][:]
    lats = nc.variables['lat'][:]
    fwi = nc.variables['fwi'][:]
    nc.close()

    lon2d, lat2d = np.meshgrid(lons, lats)

    df = pd.DataFrame({
        'latitude': lat2d.flatten(),
        'longitude': lon2d.flatten(),
        'fwi': fwi[0, :, :].flatten(),
    })

    df = df.dropna(subset=['fwi'])
    df = df.reset_index(drop=True)

    with urllib.request.urlopen(cfg.FR_GEOJSON) as url:
        dep_polygons = json.loads(url.read().decode())

    deps = [include_department(df.iloc[i], dep_polygons) for i in range(df.shape[0])]
    df['departement'] = deps
    df = df[df['departement'] != ""]
    dep_geo_df = df[['latitude', 'longitude', 'departement']]
    dep_geo_df.to_pickle(cfg.DATA_PATH + 'departement_df.pickle')


if __name__ == "__main__":
    load_data()
    create_departement_df()
