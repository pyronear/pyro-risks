import logging
import geopandas as gpd
from typing import Optional

from pyronear_ds import config as cfg

__all__ = ['get_french_geom']


def get_french_geom(path: Optional[str] = None) -> gpd.GeoDataFrame:
    """Creates the dataframe with the geometry of French departments

    Args:
        path: optional path to your local geojson
    """
    if isinstance(path, str):
        return gpd.read_file(path)
    else:
        try:
            return gpd.read_file(cfg.FR_GEOJSON)
        except Exception:
            logging.warning(f"Unable to access {cfg.FR_GEOJSON}, trying fallback.")
            return gpd.read_file(cfg.FR_GEOJSON_FALLBACK)
