import requests
import os
import gzip
import tarfile
import shutil
import warnings

from typing import Tuple, Optional

from io import BytesIO
from datetime import datetime
from urllib.parse import urlparse
from zipfile import ZipFile

import numpy as np
import pandas as pd


def get_intersection_range(ts1: pd.Series, ts2: pd.Series) -> pd.DatetimeIndex:
    """Computes the intersecting date range of two series.

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


def find_closest_weather_station(
    df_weather: pd.DataFrame, latitude: pd.DataFrame, longitude: pd.DataFrame
) -> int:
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
    if "STATION" not in df_weather.columns:
        raise ValueError("STATION column is missing in given weather dataframe.")

    weather = df_weather.drop_duplicates(subset=["STATION", "LATITUDE", "LONGITUDE"])

    zipped_station_lat_lon = zip(
        weather["STATION"].values.tolist(),
        weather["LATITUDE"].values.tolist(),
        weather["LONGITUDE"].values.tolist(),
    )
    list_station_lat_lon = list(zipped_station_lat_lon)

    reference_station = list_station_lat_lon[0][0]
    latitude_0 = list_station_lat_lon[0][1]
    longitude_0 = list_station_lat_lon[0][2]

    min_distance = np.sqrt(
        (latitude - latitude_0) ** 2 + (longitude - longitude_0) ** 2
    )

    for k in range(1, weather.shape[0]):
        current_latitude = list_station_lat_lon[k][1]
        current_longitude = list_station_lat_lon[k][2]
        current_distance = np.sqrt(
            (latitude - current_latitude) ** 2 + (longitude - current_longitude) ** 2
        )

        if current_distance < min_distance:
            min_distance = current_distance
            reference_station = list_station_lat_lon[k][0]

    return int(reference_station)


def find_closest_location(
    df_weather: pd.DataFrame, latitude: float, longitude: float
) -> Tuple[float, float]:
    """
    For a given point (`latitude`, `longitude`), get the closest point which exists in `df_weather`.
    This function is to be used when the user do not choose to use weather stations data but satellite data
    e.g. ERA5 Land variables.

    Args:
        df_weather: pd.DataFrame
            Dataframe of land/weather conditions
        latitude: float
            Latitude of the point to which we want to find the closest point in `df_weather`.
        longitude: float
            Longitude of the point to which we want to find the closest in `df_weather`.

    Returns: Tuple(float, float)
        Tuple of the closest weather point (closest_lat, closest_lon) of the point (lat, lon)
    """
    if "STATION" in df_weather.columns:
        raise ValueError(
            "STATION is in the columns, should use `find_closest_weather_station`."
        )

    weather = df_weather.drop_duplicates(subset=["latitude", "longitude"])

    zipped_points_lat_lon = zip(
        weather["latitude"].values.tolist(), weather["longitude"].values.tolist()
    )
    list_station_lat_lon = list(zipped_points_lat_lon)

    latitude_0 = list_station_lat_lon[0][0]
    longitude_0 = list_station_lat_lon[0][1]
    reference_point = (latitude_0, longitude_0)

    min_distance = np.sqrt(
        (latitude - latitude_0) ** 2 + (longitude - longitude_0) ** 2
    )

    for k in range(1, weather.shape[0]):
        current_latitude = list_station_lat_lon[k][0]
        current_longitude = list_station_lat_lon[k][1]
        current_distance = np.sqrt(
            (latitude - current_latitude) ** 2 + (longitude - current_longitude) ** 2
        )

        if current_distance < min_distance:
            min_distance = current_distance
            reference_point = (current_latitude, current_longitude)

    return reference_point


def url_retrieve(url: str, timeout: Optional[float] = None) -> bytes:
    """Retrives and pass the content of an URL request.

    Args:
        url: URL to request
        timeout: number of seconds before the request times out. Defaults to 4.

    Raises:
        requests.exceptions.ConnectionError:

    Return:
        Content of the response
    """
    response = requests.get(url, timeout=timeout, allow_redirects=True)
    if response.status_code != 200:
        raise requests.exceptions.ConnectionError(
            f"Error code {response.status_code} - could not download {url}"
        )
    return response.content


def get_fname(url: str) -> Tuple[str, str, str]:
    """Find file name, extension and compression of an archive located by an URL.

    Args:
        url: URL of the compressed archive

    Raises:
        ValueError: if URL contains more than one extension
        ValueError: if URL contains more than one compression format

    Returns:
        A tuple containing the base file name, extension and compression format
    """
    supported_compressions = ["tar", "gz", "zip"]
    supported_extensions = ["csv", "geojson", "shp", "shx", "nc"]

    archive_name = urlparse(url).path.rpartition("/")[-1]

    base = archive_name.split(".")[0]

    list_extensions = list(set(supported_extensions) & set(archive_name.split(".")))
    list_compressions = list(set(supported_compressions) & set(archive_name.split(".")))

    if len(list_extensions) == 0:
        extension = None
    elif len(list_extensions) == 1:
        extension = list_extensions[0]
    else:
        raise ValueError(f"Error {url} contains more than one extension")

    if len(list_compressions) == 0:
        compression = None

    elif len(list_compressions) == 1:
        compression = list_compressions[0]

    elif len(list_compressions) == 2:
        compression = "tar.gz"

    else:
        raise ValueError(f"Error {url} contains more than one compression format")

    return (base, extension, compression)


def download(
    url: str,
    default_extension: str,
    unzip: Optional[bool] = True,
    destination: Optional[str] = "./tmp",
):
    """Helper function for downloading, unzipping and saving compressed file from a given URL.

    Args:
        url: URL of the compressed archive
        default_extension: extension of the archive
        unzip: whether archive should be unzipped. Defaults to True.
        destination: folder where the file should be saved. Defaults to '.'.
    """
    # TODO Write case tests for zip, tar.gz, gz and uncompressed files
    # Check if the destination directory is created each if not exist
    # Check if the file are  download
    # Add print and logging statement add
    base, extension, compression = get_fname(url)
    content = url_retrieve(url)

    if unzip and compression == "zip":
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with ZipFile(BytesIO(content)) as zip_file:
            zip_file.extractall(destination)

    elif unzip and compression == "tar.gz":
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with tarfile.open(fileobj=BytesIO(content), mode="r:gz") as tar_file:
            tar_file.extractall(path=destination)

    elif unzip and compression == "gz":
        file_name = (
            f"{base}.{extension}"
            if extension is not None
            else f"{base}.{default_extension}"
        )
        full_path = os.path.join(destination, file_name)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with gzip.open(BytesIO(content)) as gzip_file, open(
            full_path, "wb+"
        ) as unzipped_file:
            shutil.copyfileobj(gzip_file, unzipped_file)

    elif not unzip and compression is None:
        file_name = (
            f"{base}.{extension}"
            if extension is not None
            else f"{base}.{default_extension}"
        )
        full_path = os.path.join(destination, file_name)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb+") as file:
            file.write(content)

    elif not unzip and isinstance(compression, str):
        file_name = f"{base}.{compression}"
        full_path = os.path.join(destination, file_name)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb+") as file:
            file.write(content)

    else:
        raise ValueError("If the file is not compressed set unzip to False")


def get_ghcn(
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    destination: Optional[str] = "./ghcn",
):
    """Download yearly Global Historical Climatology Network - Daily (GHCN-Daily) (.csv) From (NCEI).

    Args:
        start_year: first year to be retrieved. Defaults to None.
        end_year: first that will not be retrieved. Defaults to None.
        destination: destination directory. Defaults to './ghcn'.
    """
    # TODO
    # Write case tests
    # Implement archive=False
    start_year = datetime.now().year if start_year is None else start_year
    end_year = (
        datetime.now().year + 1
        if end_year is None or start_year == end_year
        else end_year
    )

    for year in range(start_year, end_year):
        url = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/{year}.csv.gz"
        download(url=url, default_extension="csv", unzip=True, destination=destination)


def get_modis(
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    yearly: Optional[bool] = False,
    destination: Optional[str] = "./firms",
):
    """Download last 24H or yearly France active fires from the FIRMS NASA.

    Args:
        start_year: first year to be retrieved. Defaults to None.
        end_year: first that will not be retrieved. Defaults to None.
        yearly: whether to download yearly active fires or not. Defaults to False.
        destination: destination directory. Defaults to './firms'.]
    """
    if yearly is True:
        start_year = datetime.now().year - 1 if start_year is None else start_year
        end_year = (
            datetime.now().year
            if end_year is None or start_year == end_year
            else end_year
        )

        for year in range(start_year, end_year):
            assert (
                start_year != 2020 or end_year != 2021
            ), "MODIS active fire archives are only available for the years from 2000 to 2019"
            url = f"https://firms.modaps.eosdis.nasa.gov/data/country/modis/{year}/modis_{year}_France.csv"
            download(
                url=url, default_extension="csv", unzip=False, destination=destination
            )

    else:
        if start_year is not None:
            raise warnings.warn(
                "The active fires from the last 24H of the MODIS Satellite will be download."
            )
        else:
            url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/MODIS_C6_Europe_24h.csv"
            download(
                url=url, default_extension="csv", unzip=False, destination=destination
            )
