import pandas as pd
import numpy as np
from netCDF4 import Dataset

import requests
import zipfile
import os
import urllib.request
import json
import logging

from shapely.geometry import Point
from shapely import geometry

from pyronear_ds import config as cfg


def load_data(source_path=None, output_path=cfg.DATA_PATH):
    """Load FWI zipped data from github repo and unzip data in folder output_path"""
    if not isinstance(source_path, str):
        source_path = cfg.FR_FWI_2019_FALLBACK
    results = requests.get(source_path)

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


def get_fwi_data(source_path=cfg.DATA_PATH, day='20190101'):
    """Load and handle netcdf data for selected day.

    Return pandas dataframe with longitude, latitude, day and fwi indices
    (fwi, ffmc, dmc, dc, isi, bui, dsr, dr).

    Args:
        source_path (str, optional): path with unzipped netcdf fwi data. Defaults to cfg.DATA_PATH.
        day (str, optional): which day to load. Defaults to '20190101'.

    Returns:
        pd.DataFrame: dataframe with all fwi indices for selected day
    """

    nc = Dataset(source_path + 'fwi_unzipped/JRC_FWI_{}.nc'.format(day), 'r')
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


def create_departement_df(day_data=get_fwi_data(), output_path=cfg.DATA_PATH):
    """Create dataframe with lon, lat coordinates and corresponding departments.

    Input: one day of FWI data previously loaded with function load_data.
    Load the json with the department polygons and run function include_department to get the
    name of departments corresponding to each row of day_data.
    Save in source_path dataframe with lat, lon points having non-empty departments.

    This may take a few minutes.

    Args:
        day_data (pd.Dataframe): where to find the netcdf from the load_data step.
        output_path (str, optional): Defaults to config.DATA_PATH.
    """
    df = day_data.copy()

    with urllib.request.urlopen(cfg.FR_GEOJSON) as url:
        dep_polygons = json.loads(url.read().decode())

    deps = [include_department(df.iloc[i], dep_polygons) for i in range(df.shape[0])]
    df['departement'] = deps
    df = df[df['departement'] != ""]
    dep_geo_df = df[['latitude', 'longitude', 'departement']]
    dep_geo_df.to_pickle(os.path.join(output_path, 'departement_df.pickle'))


class GwisFwi(pd.DataFrame):
    """FWI dataset (8 km resolution) on French territory based on 2019-2020 data.

    Concatenate fwi indices data from source_path corresponding to days_list and
    join french department.
    Attention: load_data and create_department_df must be run before initializing this class

    Args:
        source_path: str, path to saved netcdf data obtained with load_data()
        days_list: list of str, format year month day (all concatenated)
    """

    def __init__(self, source_path=cfg.DATA_PATH, days_list=['20190101']):

        fwi_df = pd.DataFrame(columns=['latitude', 'longitude', 'day',
                                       'fwi', 'ffmc', 'dmc', 'dc', 'isi', 'bui', 'dsr', 'dr'])

        if not os.path.isdir(source_path + 'fwi_unzipped/'):
            logging.warning("You must load FWI data, please run load_data")

        for day in days_list:
            df = get_fwi_data(source_path=source_path, day=day)
            fwi_df = pd.concat([fwi_df, df])

        if not os.path.isfile(source_path + 'departement_df.pickle'):
            logging.warning("Department dataframe is needed, please run create_departement_df")
        dep_geo_df = pd.read_pickle(source_path + 'departement_df.pickle')
        fwi_df = pd.merge(fwi_df, dep_geo_df, on=['latitude', 'longitude'])
        super().__init__(fwi_df)


if __name__ == "__main__":
    load_data()
    create_departement_df()
