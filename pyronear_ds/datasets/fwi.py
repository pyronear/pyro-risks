import pandas as pd
import numpy as np
from netCDF4 import Dataset

import requests
import zipfile
import os
import urllib.request
import json
import logging
import tempfile

from shapely.geometry import Point
from shapely import geometry

from pyronear_ds import config as cfg


def load_data(output_path):
    """Load FWI zipped data from github repo and unzip data in folder output_path.

    Args:
        output_path (str): absolute, relative or temporary path
    """
    results = requests.get(cfg.FR_FWI_2019_FALLBACK)

    os.makedirs(output_path, exist_ok=True)
    with open(os.path.join(output_path, 'fwi_folder.zip'), 'wb') as f:
        f.write(results.content)

    file = zipfile.ZipFile(os.path.join(output_path, 'fwi_folder.zip'))
    file.extractall(path=os.path.join(output_path, 'fwi_unzipped'))


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


def get_fwi_data(source_path, day='20190101'):
    """Load and handle netcdf data for selected day.

    Return pandas dataframe with longitude, latitude, day and fwi indices
    (fwi, ffmc, dmc, dc, isi, bui, dsr, dr).
    Args:
        source_path (str): path with unzipped netcdf fwi data, usually got from load_data.
        day (str, optional): which day to load. Defaults to '20190101'.

    Returns:
        pd.DataFrame: dataframe with all fwi indices for selected day
    """
    nc = Dataset(os.path.join(source_path, 'fwi_unzipped/JRC_FWI_{}.nc'.format(day)), 'r')
    try:
        lons = nc.variables['lon'][:]
        lats = nc.variables['lat'][:]
        fwi = nc.variables['fwi'][:]
        ffmc = nc.variables['ffmc'][:]
        dmc = nc.variables['dmc'][:]
        dc = nc.variables['dc'][:]
        isi = nc.variables['isi'][:]
        bui = nc.variables['bui'][:]
        dsr = nc.variables['dsr'][:]
        dr = nc.variables['danger_risk'][:]
    except KeyError:
        print('Some reading error with: ', day)
    nc.close()

    lon2d, lat2d = np.meshgrid(lons, lats)

    df = pd.DataFrame({
        'latitude': lat2d.flatten(),
        'longitude': lon2d.flatten(),
        'day': day,
        'fwi': fwi[0, :, :].flatten(),
        'ffmc': ffmc[0, :, :].flatten(),
        'dmc': dmc[0, :, :].flatten(),
        'dc': dc[0, :, :].flatten(),
        'isi': isi[0, :, :].flatten(),
        'bui': bui[0, :, :].flatten(),
        'dsr': dsr[0, :, :].flatten(),
        'dr': dr[0, :, :].flatten(),
    })
    df = df.dropna(subset=['fwi', 'ffmc', 'dmc', 'dc', 'isi', 'bui', 'dsr', 'dr'])
    df = df.reset_index(drop=True)
    return df


def create_departement_df(day_data):
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
    df['departement'] = deps
    df = df[df['departement'] != ""]
    dep_geo_df = df[['latitude', 'longitude', 'departement']]
    return dep_geo_df


class GwisFwi(pd.DataFrame):
    """GWIS FWI dataframe (8 km resolution) on French territory based on 2019-2020 data."""

    def __init__(self, days_list=['20190101']):
        """Create dataframe with fwi indices data corresponding to days_list and join french department.

        Args:
            days_list: list of str, format year month day (all concatenated)
        """
        fwi_df = pd.DataFrame(columns=['latitude', 'longitude', 'day',
                                       'fwi', 'ffmc', 'dmc', 'dc', 'isi', 'bui', 'dsr', 'dr'])
        with tempfile.TemporaryDirectory() as tmp:
            load_data(output_path=tmp)
            for day in days_list:
                df = get_fwi_data(source_path=tmp, day=day)
                fwi_df = pd.concat([fwi_df, df])
            dep_geo_df = create_departement_df(df)
            fwi_df = pd.merge(fwi_df, dep_geo_df, on=['latitude', 'longitude'])
        super().__init__(fwi_df)
