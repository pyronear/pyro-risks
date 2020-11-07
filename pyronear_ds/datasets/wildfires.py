import logging
import pandas as pd
from typing import List, Optional


from pyronear_ds import config as cfg

__all__ = ['BDIFFHistory']


class BDIFFHistory(pd.DataFrame):
    """Wildfire history dataset on French territory, accessible at https://bdiff.agriculture.gouv.fr/.

    Args:
        source_path: path or URL to your version of the source data
        use_cols: columns to read from source
    """

    kept_cols = ['Date de première alerte', 'Département', 'Statut']

    def __init__(self, source_path: Optional[str] = None, use_cols: Optional[List[str]] = None) -> None:
        if not isinstance(source_path, str):
            # Download in cache
            logging.warning(f"No data source specified for {self.__class__.__name__}, trying fallback.")
            source_path = cfg.FR_FIRES_FALLBACK
        if not isinstance(use_cols, list):
            use_cols = self.kept_cols
        data = pd.read_csv(source_path, sep=";", usecols=use_cols)
        tmp = pd.to_datetime(data['Date de première alerte'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
        data['date'] = tmp.dt.normalize()  # Set time to 00:00:00 for each entry
        # Drop Cols
        super().__init__(data.drop(['Date de première alerte'], axis=1))
