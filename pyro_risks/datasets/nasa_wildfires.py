import logging
from typing import List, Optional

import geopandas as gpd
import pandas as pd

from pyro_risks import config as cfg

__all__ = ["NASAFIRMS"]

from .masks import get_french_geom


class NASAFIRMS(pd.DataFrame):
    """Wildfire history dataset on French territory, using data from
    NASA satellites. Accessible by completing the form at
    https://effis.jrc.ec.europa.eu/applications/data-request-form/

    Careful when completing the form, you can either choose to get the
    dataset in json format or xlsx format.
    However if your source data is in a csv format, you can still use
    this class to clean it using the parameter `fmt`.

    By default, the format is considered to be json.

    Args:
        source_path: str
            Path or URL to your version of the source data
        fmt: str
            Format of the source data, can either be "csv", "xlsx"
            or "json". Default is "json".
        use_cols: List[str]
            List of columns to read from the source
    """

    kept_cols = [
        "latitude",
        "longitude",
        "acq_date",
        "acq_time",
        "confidence",
        "bright_t31",
        "frp",
    ]
    fmt = "json"

    def __init__(
        self,
        source_path: Optional[str] = None,
        fmt: Optional[str] = None,
        use_cols: Optional[List[str]] = None,
    ) -> None:
        """
        Args:
            source_path: Optional[str]
                Path or URL to your version of the source data
            fmt: Optional[str]
                Format of the source data, can either be
                "csv", "xlsx" or "json".
            use_cols: Optional[List[str]]
                List of columns to keep in the dataframe
        """
        if not isinstance(source_path, str):
            # Download in cache
            logging.warning(
                f"No data source specified for {self.__class__.__name__}, trying fallback."
            )
            source_path = cfg.FR_NASA_FIRMS_FALLBACK
        if not isinstance(fmt, str):
            fmt = self.fmt
        if not isinstance(use_cols, list):
            use_cols = self.kept_cols

        if fmt == "json":
            data = pd.read_json(source_path, orient="records")
            data = pd.json_normalize(data["features"])
            # remove unnecessary prefix
            data.columns = [col.split(".")[-1] for col in data.columns]
            # keep defined columns
            data = data[use_cols]

        elif fmt == "xlsx":
            data = pd.read_excel(source_path, usecols=use_cols)

        elif fmt == "csv":
            data = pd.read_csv(source_path, usecols=use_cols)
            # if csv format, the `acq_time` column needs to be changed
            # the raw data as the format "HHMM", we will transform it
            # so that it has the format "HHMMSS"
            # convert type to str
            data["acq_time"] = data["acq_time"].astype(str)
            # fill with 0
            data["acq_time"] = data["acq_time"].str.ljust(6, "0")
            # prepare for datetime needs
            data["acq_time"] = data["acq_time"].apply(
                lambda s: ":".join(map("{}{}".format, *(s[::2], s[1::2])))
            )

        else:
            raise ValueError(
                "The given format cannot be read, it should be either csv, xlsx or json."
            )

        data["acq_date_time"] = data["acq_date"] + " " + data["acq_time"]
        data["acq_date"] = pd.to_datetime(
            data["acq_date"], format="%Y-%m-%d", errors="coerce"
        )
        data["acq_date_time"] = pd.to_datetime(
            data["acq_date_time"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
        )
        data["latitude"] = data["latitude"].astype(float)
        data["longitude"] = data["longitude"].astype(float)
        data["bright_t31"] = data["bright_t31"].astype(float)
        data["frp"] = data["frp"].astype(float)

        # add departements geometry to allow for departements merging
        geo_data = gpd.GeoDataFrame(
            data,
            geometry=gpd.points_from_xy(data["longitude"], data["latitude"]),
            crs="EPSG:4326",
        )
        # Match the polygons using the ones of each predefined country area
        geo_masks = get_french_geom()
        geo_df = gpd.sjoin(geo_masks, geo_data, how="inner")
        super().__init__(geo_df.drop(["acq_time", "index_right", "geometry"], axis=1))
