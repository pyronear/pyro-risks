from datetime import date
from pyro_risks.utils.fwi_helpers import FWIHelpers
from pyro_risks.utils.s3 import S3Bucket
import os


def main():
    # AWS credentials and config paths
    aws_path = "../../../../.aws/"
    aws_credentials_path = aws_path + "credentials"
    aws_config_path = aws_path + "config"

    # Get AWS credentials
    with open(aws_credentials_path) as f:
        content = f.read().splitlines()
        my_access_key_id = content[1].split(" = ")[1]
        my_secret_access_key = content[2].split(" = ")[1]

    # Get AWS config
    with open(aws_config_path) as f:
        content = f.read().splitlines()
        my_endpoint = content[8].split(" = ")[1]

    # Create an S3Bucket instance
    s3 = S3Bucket(
        bucket_name="risk",
        endpoint_url=my_endpoint,
        region_name="gra",
        aws_access_key_id=my_access_key_id,
        aws_secret_key=my_secret_access_key,
    )

    today_date_str_url = date.today().strftime("%Y-%m-%d")
    effis_tiff_file_url = (
        "https://ies-ows.jrc.ec.europa.eu/effis?LAYERS=ecmwf007.fwi&FORMAT=image/tiff&TRANSPARENT=true&SINGLETILE=false&SERVICE=wms&VERSION=1.1.1&REQUEST=GetMap&STYLES=&SRS=EPSG:4326&BBOX=-6.0,41.0,10.0,52.0&WIDTH=1600&HEIGHT=1200&TIME="
        + today_date_str_url
    )

    today_date_str_url = date.today().strftime("%Y_%m_%d")
    filename_in_bucket = "fwi_" + today_date_str_url + ".tiff"

    # Download file from EFFIS and convert it to a geodf
    fwi = FWIHelpers()
    gdf_fwi = fwi.get_fwi(effis_tiff_file_url)
    gdf_fwi = fwi.fwi_sea_remover(gdf_fwi)
    gdf_fwi["fwi_category"] = gdf_fwi.apply(
        lambda row: fwi.fwi_category(row["fwi_pixel_value"]), axis=1
    )
    gdf_fwi = gdf_fwi.drop("fwi_pixel_value", axis=1)

    new_json_fwi = fwi.fwi_geojson_maker(gdf_fwi)

    today_date_str_url = date.today().strftime("%Y_%m_%d")
    filepath_in_bucket = "fwi/fwi_" + today_date_str_url + ".geojson"

    # Upload the JSON data to Github

    # Store the JSON data to S3
    s3.write_json_to_s3(object_key=filepath_in_bucket, json_data=new_json_fwi)


if __name__ == "__main__":
    main()
