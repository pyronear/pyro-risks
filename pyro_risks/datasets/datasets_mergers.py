import pandas as pd

from .utils import (
    find_closest_weather_station,
    find_closest_location,
    get_nearest_points,
)


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


def merge_datasets_by_closest_weather_point(
    df_weather: pd.DataFrame,
    time_col_weather: str,
    df_fires: pd.DataFrame,
    time_col_fires: str,
) -> pd.DataFrame:
    """
    Merge weather and fire datasets when the weather dataset is provided using satellite
    data such as ERA5 Land hourly dataset provided here
    https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=form
    and accessible through cdsapi.

    Args:
        df_weather: pd.DataFrame
            Weather conditions dataframe, must have "latitude" and "longitude" columns.
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
    df_fires["closest_weather_point"] = df_fires.apply(
        lambda row: find_closest_location(
            df_weather, row["latitude"], row["longitude"]
        ),
        axis=1,
    )

    grouped_fires = (
        df_fires.groupby(["closest_weather_point", "acq_date"], observed=True)
        .first()
        .reset_index()
    )

    grouped_fires["weather_lat"], grouped_fires["weather_lon"] = (
        grouped_fires["closest_weather_point"].str[0],
        grouped_fires["closest_weather_point"].str[1],
    )

    merged_data = pd.merge(
        df_weather,
        grouped_fires,
        left_on=[time_col_weather, "latitude", "longitude"],
        right_on=[time_col_fires, "weather_lat", "weather_lon"],
        how="left",
    )
    return merged_data


def merge_by_proximity(
    df_left: pd.DataFrame,
    time_col_left: str,
    df_right: pd.DataFrame,
    time_col_right: str,
    how: str,
) -> pd.DataFrame:
    """
    Merge df_left and df_right by finding in among all points in df_left, the closest point in df_right.
    For instance, df_left can be a history wildfires dataset and df_right a weather conditions datasets and
    we want to match each wildfire with its closest weather point.
    This can also be used if, for instance, we want to merge FWI dataset (df_left) with ERA5/VIIRS datatset
    (df_right).

    Args:
        df_left: pd.DataFrame
            Left dataframe, must have "latitude" and "longitude" columns.
        time_col_left: str
            Name of the time column in `df_left`.
        df_right: pd.DataFrame
            Right dataset, must have points described by their latitude and
            longitude.
        time_col_right: str
            Name of the time column in `df_right`.
        how: str
            How the pandas merge needs to be done.

    Returns:
        Merged dataset by point (lat/lon) proximity.
    """
    df_left = df_left.reset_index(drop=True)
    df_right = df_right.reset_index(drop=True)

    # get all df_right points in adequate format
    df_tmp = df_right.drop_duplicates(subset=["latitude", "longitude"])
    lat_right = df_tmp["latitude"].values
    lon_right = df_tmp["longitude"].values
    candidates = list(zip(lat_right, lon_right))

    df_tmp2 = df_left.drop_duplicates(subset=["latitude", "longitude"])
    source_points = list(zip(df_tmp2["latitude"].values, df_tmp2["longitude"].values))

    indices, _ = get_nearest_points(source_points, candidates)

    dict_idx_lat_lon = {}
    for idx in set(indices):
        df_tmp = df_right[df_right.index == idx]
        dict_idx_lat_lon[idx] = (
            df_tmp["latitude"].values[0],
            df_tmp["longitude"].values[0],
        )

    dict_source_idx = dict(zip(source_points, indices))

    df_left["point"] = list(zip(df_left["latitude"], df_left["longitude"]))

    df_left["corresponding_index"] = df_left["point"].map(dict_source_idx)

    df_left["closest_point"] = df_left["corresponding_index"].map(dict_idx_lat_lon)

    df_left["closest_lat"], df_left["closest_lon"] = (
        df_left["closest_point"].str[0],
        df_left["closest_point"].str[1],
    )

    merged_data = pd.merge(
        df_left,
        df_right,
        left_on=[time_col_left, "closest_lat", "closest_lon"],
        right_on=[time_col_right, "latitude", "longitude"],
        how=how,
    )

    merged_data = merged_data.drop(
        ["point", "closest_point", "corresponding_index"], axis=1
    )
    return merged_data
