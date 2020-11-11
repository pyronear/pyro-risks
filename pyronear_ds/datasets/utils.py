import numpy as np
import pandas as pd


def get_intersection_range(ts1: pd.Series, ts2: pd.Series) -> pd.DatetimeIndex:
    """Computes the intersecting date range of two series

    Args:
        ts1: time series
        ts2: time series
    """

    # Time span selection
    time_range1 = max(ts1.min(), ts2.min())
    time_range2 = min(ts1.max(), ts2.max())
    if time_range1 > time_range2:
        raise ValueError("Extracts do not have intersecting date range")

    return pd.date_range(time_range1, time_range2)


def find_closest_weather_station(df_weather, latitude, longitude):
    """
    The weather dataframe SHOULD contain a "STATION" column giving the id of
    each weather station in the dataset.

    Args:
        df_weather: pd.DataFrame
            Dataframe of weather conditions
        latitude: float
            Latitude of the point to which we want to find the closest
            weather station
        longitude: float
            Longitude of the point to which we want to find the closest
            weather station

    Returns: int
        Id of the closest weather station of the point (lat, lon)

    """
    if 'STATION' not in df_weather.columns:
        raise ValueError("STATION column is missing in given weather dataframe.")

    weather = df_weather.drop_duplicates(subset=['STATION', 'LATITUDE', 'LONGITUDE'])

    zipped_station_lat_lon = zip(
        weather['STATION'].values.tolist(),
        weather['LATITUDE'].values.tolist(),
        weather['LONGITUDE'].values.tolist()
    )
    list_station_lat_lon = list(zipped_station_lat_lon)

    reference_station = list_station_lat_lon[0][0]
    latitude_0 = list_station_lat_lon[0][1]
    longitude_0 = list_station_lat_lon[0][2]

    min_distance = np.sqrt((latitude - latitude_0) ** 2 + (longitude - longitude_0) ** 2)

    for k in range(1, weather.shape[0]):
        current_latitude = list_station_lat_lon[k][1]
        current_longitude = list_station_lat_lon[k][2]
        current_distance = np.sqrt((latitude - current_latitude) ** 2 + (longitude - current_longitude) ** 2)

        if current_distance < min_distance:
            min_distance = current_distance
            reference_station = list_station_lat_lon[k][0]

    return int(reference_station)
