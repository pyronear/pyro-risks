from dotenv import load_dotenv
import os
import datetime
import geopandas as gpd
from shapely.geometry import Point, Polygon
from pyrorisks.utils.s3 import S3Bucket
from typing import Dict, Any
from pyrorisks.utils.fwi_helpers import FWIHelpers

__all__ = ["get_score"]


def point_fwi_category(row, point_coords):
    if row["geometry"].contains(point_coords):
        return row["fwi_category"]
    else:
        return None


def get_score(lat, lon):
    point_coords = Point(lon, lat)

    load_dotenv()

    s3 = S3Bucket(
        bucket_name=os.environ["BUCKET_NAME"],
        endpoint_url=os.environ["ENDPOINT_URL"],
        region_name=os.environ["REGION_NAME"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
        aws_secret_key=os.environ["AWS_SECRET_KEY"],
    )

    retrieved_date = datetime.date.today().strftime("%Y-%m-%d")
    year, month, day = retrieved_date.split("-")

    json_content = s3.read_json_from_s3(
        object_key=f"fwi/year={year}/month={month}/day={day}/fwi_values.json",
    )

    gdf = gpd.GeoDataFrame.from_features(json_content["features"])

    gdf["fwi_category_for_point"] = gdf.apply(lambda row: point_fwi_category(row, point_coords), axis=1)
    point_fwi_score = gdf.dropna().iloc[0]["fwi_category"]
    return point_fwi_score

def get_fwi(longitude: float, latitude: float, crs: str = "EPSG:4326", date: str = None) -> Dict[str, Any]:
    today_date_str_url = datetime.date.today().strftime('%Y-%m-%d') if date is None else date
    effis_tiff_file_url = "https://ies-ows.jrc.ec.europa.eu/effis?LAYERS=ecmwf007.fwi&FORMAT=image/tiff&TRANSPARENT=true&SINGLETILE=false&SERVICE=wms&VERSION=1.1.1&REQUEST=GetMap&STYLES=&SRS=EPSG:4326&BBOX=-6.0,41.0,10.0,52.0&WIDTH=1600&HEIGHT=1200&TIME="+today_date_str_url
    fwi = FWIHelpers()
    point = Point(longitude, latitude)
    gdf_fwi =  fwi.get_fwi(effis_tiff_file_url)
    gdf_fwi["fwi_category"] = gdf_fwi.apply(lambda row: fwi.fwi_category(row["fwi_pixel_value"]), axis=1)
    gdf_fwi["fwi_category_for_point"] = gdf_fwi.apply(lambda row: point_fwi_category(row, point), axis=1)
    gdf_fwi = gdf_fwi.drop("fwi_pixel_value", axis=1)
    point_fwi_score = gdf_fwi.dropna().iloc[0]["fwi_category"]

    results = {"longitude":longitude, "latitude":latitude, "crs":crs, "score": "fwi", "value": float(point_fwi_score),"date": today_date_str_url}
    return results