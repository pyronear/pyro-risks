import pandas as pd

from .utils import find_closest_weather_station


def merge_datasets_by_departements(
    dataframe1: pd.DataFrame,
    time_col1: str,
    geometry_col1: str,
    dataframe2: pd.DataFrame,
    time_col2: str,
    geometry_col2: str,
    how: str,
) -> pd.DataFrame:
    """
    Merge two datasets containing some kind of geometry and date columns.
    The merge is down on [time_col1, time_col2] and [geometry_col1, geometry_col2].
    Here the geometry is based on French departements. Therefore the geometry columns
    should contains either the code on the departement or its geometry (should be
    consistent throughout both datasets).

    Finally the merge is done according to the `how` parameter. Keep me mind that
    this parameter must be so that the merged dataframe keeps similar dimensions to the
    weather dataframe. This is because if there is an inner join, we will keep only the days
    where wildfires were declared. Therefore if the weather dataframe is the left frame, then
    `how` must be left, if it is the right frame, `how` must be right.

    Args:
        dataframe1: pd.DataFrame
            First dataframe, containing a time column and a geometry one.
        time_col1: str
            Name of the time column of dataframe1 on which the merge will be done.
        geometry_col1: str
            Name of the geometry column of dataframe1 on which the merge will be done.
        dataframe2: pd.DataFrame
            Second dataframe, containing a time column and a geometry one.
        time_col2: str
            Name of the time column of dataframe2 on which the merge will be done.
        geometry_col2: str
            Name of the geometry column of dataframe2 on which the merge will be done.
        how:
            Parameter of the merge, should correspond to which of the left or right frame
            the weather dataframe is.

    Returns: pd.DataFrame
        Merged dataset on French departement.
    """
    merged_data = pd.merge(
        dataframe1,
        dataframe2,
        left_on=[time_col1, geometry_col1],
        right_on=[time_col2, geometry_col2],
        how=how,
    )
    return merged_data


def merge_datasets_by_closest_weather_station(
    df_weather: pd.DataFrame,
    time_col_weather: str,
    df_fires: pd.DataFrame,
    time_col_fires: str,
) -> pd.DataFrame:
    """
    Merge two datasets: one of weather conditions and the other of wildfires history data.
    Each dataset must contain a time column, and the weather dataset must have a `STATION`
    column which allows to identify uniquely each station. The merge is done by finding the
    closest weather station to each (lat, lon) point of the wildfires history dataset. The
    latter is then grouped by date and closest_weather_station, which then allows to join it
    with the weather conditions dataframe.

    Args:
        df_weather: pd.DataFrame
            Weather conditions dataframe. Must have a `STATION` column to identify each
            weather station.
        time_col_weather: str
            Name of the time column in `df_weather`.
        df_fires: pd.DataFrame
            Wildfires history dataset, must have points described by their latitude and
            longitude.
        time_col_fires: str
            Name of the time column in `df_fires`.

    Returns: pd.DataFrame
        Merged dataset by weather station proximity.
    """
    # For wildfires dataframe, need to find for each point the closest weather station
    df_fires["closest_weather_station"] = df_fires.apply(
        lambda row: find_closest_weather_station(
            df_weather, row["latitude"], row["longitude"]
        ),
        axis=1,
    )

    grouped_fires = (
        df_fires.groupby(["closest_weather_station", "acq_date"], observed=True)
        .first()
        .reset_index()
    )

    merged_data = pd.merge(
        df_weather,
        grouped_fires,
        left_on=[time_col_weather, "STATION"],
        right_on=[time_col_fires, "closest_weather_station"],
        how="left",
    )
    return merged_data
