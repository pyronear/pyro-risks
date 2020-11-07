import logging
import pandas as pd
from typing import List, Optional

from pyronear_ds import config as cfg


__all__ = ['NASAFIRMS']


class NASAFIRMS(pd.DataFrame):
    """
    Wildfire history dataset on French territory, using data from
    NASA satellites. Accessible by completing the form at
    https://effis.jrc.ec.europa.eu/applications/data-request-form/

    Careful when completing the form, you can either choose to get the
    dataset in json format or xlsx format.
    However if your source data is in a csv format, you can still use
    this class to clean it.

    By default, the format is considered to be json.

    Args:
        source_path: str
            path or URL to your version of the source data
        use_cols: List[str]
            List of columns to read from the source
        format: str
            Format of the source data, can either be "csv", "xlsx"
            or "json". Default is "json".
    """

    kept_cols = ['latitude', 'longitude', 'acq_date', 'acq_time', 'confidence', 'bright_t31', 'frp']
    fmt = 'json'

    def __init__(self, source_path: Optional[str] = None, use_cols: Optional[List[str]] = None,
                 format: Optional[str] = None) -> None:
        if not isinstance(source_path, str):
            # Download in cache
            logging.warning(f"No data source specified for {self.__class__.__name__}, trying fallback.")
            source_path = cfg.FR_FIRES_FALLBACK
            #source_path = '/Users/chloesekkat/Documents/pyronear-datascience/pyronear_ds/data/NASA_FIRMS.json'
        if not isinstance(use_cols, list):
            use_cols = self.kept_cols
        if not isinstance(format, str):
            format = self.fmt

        if format == 'json':
            data = pd.read_json(source_path)
            data = pd.json_normalize(data['features'])
            # remove unnecessary prefix
            data.columns = [col.split('.')[-1] for col in data.columns]
            # keep defined columns
            data = data[use_cols]

        elif format == "xlsx":
            data = pd.read_excel(source_path, usecols=use_cols)

        elif format == "csv":
            data = pd.read_csv(source_path, usecols=use_cols)

        data['acq_date_time'] = data['acq_date'] + " " + data['acq_time']
        data['acq_date'] = pd.to_datetime(data['acq_date'], format="%Y-%m-%d", errors="coerce")
        data['acq_date_time'] = pd.to_datetime(data['acq_date_time'], format="%Y-%m-%d %H:%M:%S", errors="coerce")

        super().__init__(data.drop(['acq_time'], axis=1))
