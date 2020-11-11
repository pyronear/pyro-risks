import pandas as pd
import numpy as np
from netCDF4 import Dataset

from pyronear_ds import config as cfg


class GwisFwi(pd.DataFrame):
    """FWI dataset (8 km resolution) on French territory based on 2019-2020 data received via
    personal communication. Concatenate fwi indices data from source_path corresponding to days_list and
    join french department.

    Attention: fwi_utils.py must be run before to initialize this class

    Args:
        source_path: str, path to saved netcdf data obtained with load_data()
        days_list: list of str, format year month day (all concatenated)
    """

    def __init__(self, source_path=cfg.DATA_PATH, days_list=['20190101']):

        fwi_df = pd.DataFrame(columns=['latitude', 'longitude', 'day',
                                       'fwi', 'ffmc', 'dmc', 'dc', 'isi', 'bui', 'dsr', 'dr'])

        for day in days_list:
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
                continue
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
            fwi_df = pd.concat([fwi_df, df])

        dep_geo_df = pd.read_pickle(source_path + 'departement_df.pickle')
        fwi_df = pd.merge(fwi_df, dep_geo_df, on=['latitude', 'longitude'])
        super().__init__(fwi_df)
