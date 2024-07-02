import rasterio
from rasterio.features import shapes
import geopandas as gpd
import requests
from io import BytesIO
import json
from typing import Optional


class FWIHelpers:
    """
    A class for handling the FWI GeoTIFF we get from EFFIS.
    """

    def __init__(self) -> None:
        """
        Initializes the FWI_Helpers class.
        """
        rasterio.Env()

    def get_fwi(self, tiff_url: str) -> Optional[gpd.GeoDataFrame]:
        """
        Retrieves Fire Weather Index (FWI) data from a GeoTIFF file hosted at a given URL.

        This function downloads a GeoTIFF file from the provided URL, converts it to a GeoDataFrame
        containing FWI information, and returns the resulting GeoDataFrame.

        Args:
            tiff_url (str): The URL of the GeoTIFF file to retrieve FWI data from.

        Returns:
            geopandas.GeoDataFrame or None: A GeoDataFrame containing FWI data if successful,
            or None if an error occurs during the retrieval or conversion.
        """
        try:
            response = requests.get(tiff_url, stream=True)
            mask = None
            data = rasterio.open(BytesIO(response.content)).meta

            with rasterio.open(BytesIO(response.content)) as src:
                image = src.read(1)  # first band
                results = (
                    {"properties": {"fwi_pixel_value": v}, "geometry": s}
                    for i, (s, v) in enumerate(
                        shapes(image, mask=mask, transform=data["transform"])
                    )
                )

            geoms = list(results)
            gpd_polygonized_raster = gpd.GeoDataFrame.from_features(
                geoms, crs=str(data["crs"])
            )
            return gpd_polygonized_raster

        except Exception as e:
            print(f"Error: {e}")
            return None

    def fwi_sea_remover(self, geodataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Removes the sea from the dataset (FWI pixel value = 0).

        Args:
            geodataframe (geopandas.GeoDataFrame): The GeoDataFrame we reomve the sea from.

        Returns:
            geodataframe (geopandas.GeoDataFrame): The GeoDataFrame without the sea.
        """
        geodataframe = geodataframe.loc[
            (geodataframe["fwi_pixel_value"] != 0)
        ]  # remove the sea
        return geodataframe

    def fwi_category(self, fwi_pixel_val: int) -> int:
        """
        Categorizes FWI pixel values from GeoTIFF into fire risk categories (from low to very extreme).

        Args:
            fwi_pixel_val (int): The Fire Weather Index (FWI) pixel value to categorize.

        Returns:
            risk_value (int): The risk assesment FWI pixel value, from 1 to 6 with :
                                - 1 : low
                                - 2 : moderate
                                - 3 : high
                                - 4 : very high
                                - 5 : extreme
                                - 6 : very extreme
        """
        # TODO: use a `dict`
        categories = [
            (58, 6),
            (145, 1),
            (192, 5),
            (210, 2),
            (231, 4),
        ]

        for threshold, risk_value in categories:
            if fwi_pixel_val <= threshold:
                return risk_value

        return 3

    def fwi_geojson_maker(self, geodataframe: gpd.GeoDataFrame) -> json:
        """
        Converts a GeoDataFrame into a GeoJSON.

        This function takes a GeoDataFrame and turns it into a GeoJSON by removing
        index field and reformatting it. The resulting GeoJSON includes only the
        essential properties and the CRS information.

        Args:
            geodataframe (geopandas.GeoDataFrame): The GeoDataFrame to be converted into GeoJSON.

        Returns:
            new_json_fwi: A GeoJSON representation of the input GeoDataFrame with essential
                properties and CRS information.
        """
        json_fwi = geodataframe.to_json()
        json_fwi = json.loads(json_fwi)
        for feature_dict in json_fwi["features"]:
            del feature_dict["id"]
        new_json_fwi = {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
            },
            "features": json_fwi["features"],
        }
        return new_json_fwi
