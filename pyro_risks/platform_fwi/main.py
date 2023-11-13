# Usual Imports
import os
from datetime import date
from dotenv import load_dotenv

# Pyro Risks Imports
from pyro_risks.utils.fwi_helpers import FWIHelpers
from pyro_risks.utils.s3 import S3Bucket


def main():
    load_dotenv()
    # Create an S3Bucket instance
    s3 = S3Bucket(
        bucket_name=os.environ["BUCKET_NAME"],
        endpoint_url=os.environ["ENDPOINT_URL"],
        region_name=os.environ["REGION_NAME"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
        aws_secret_key=os.environ["AWS_SECRET_KEY"],
    )

    # Get the FWI GeoJSON from EFFIS
    today_date_str_url = date.today().strftime("%Y-%m-%d")
    effis_tiff_file_url = (
        "https://ies-ows.jrc.ec.europa.eu/effis?LAYERS=ecmwf007.fwi&FORMAT=image/tiff&TRANSPARENT=true&SINGLETILE=false&SERVICE=wms&VERSION=1.1.1&REQUEST=GetMap&STYLES=&SRS=EPSG:4326&BBOX=-6.0,41.0,10.0,52.0&WIDTH=1600&HEIGHT=1200&TIME="
        + today_date_str_url
    )

    # Download file from EFFIS and convert it to a geodf
    fwi = FWIHelpers()
    gdf_fwi = fwi.get_fwi(effis_tiff_file_url)
    gdf_fwi = fwi.fwi_sea_remover(gdf_fwi)
    gdf_fwi["fwi_category"] = gdf_fwi.apply(
        lambda row: fwi.fwi_category(row["fwi_pixel_value"]), axis=1
    )
    gdf_fwi = gdf_fwi.drop("fwi_pixel_value", axis=1)

    new_json_fwi = fwi.fwi_geojson_maker(gdf_fwi)

    # Store the JSON data to S3
    year, month, day = today_date_str_url.split("-")
    s3.write_json_to_s3(
        object_key=f"fwi/year={year}/month={month}/day={day}/fwi_values.json",
        json_data=new_json_fwi,
    )


if __name__ == "__main__":
    main()
