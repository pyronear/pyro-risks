from pyro_risks.utils.s3 import S3Bucket
from dotenv import load_dotenv
import os
from datetime import date
import geopandas as gpd
from shapely.geometry import Point


def get_score(lat, lon):
    point_coords = Point(lat, lon)

    load_dotenv()

    s3 = S3Bucket(
        bucket_name=os.environ["BUCKET_NAME"],
        endpoint_url=os.environ["ENDPOINT_URL"],
        region_name=os.environ["REGION_NAME"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
        aws_secret_key=os.environ["AWS_SECRET_KEY"],
    )

    retrieved_date = date.today().strftime("%Y-%m-%d")
    year, month, day = retrieved_date.split("-")

    json_content = s3.read_json_from_s3(
        object_key=f"fwi/year={year}/month={month}/day={day}/fwi_values.json",
    )

    gdf = gpd.GeoDataFrame.from_features(json_content["features"])
    point_fwi_score = gpd.sjoin(gdf, point_coords, how="inner", op="within").iloc[0][
        "fwi_category"
    ]
    return point_fwi_score
