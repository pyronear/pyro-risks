from dataclasses import dataclass

from pandas import DataFrame


@dataclass
class GeographicData:
    dataframe: DataFrame
    time_col: str
    geometry_col: str
