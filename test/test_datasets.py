import unittest

import numpy as np
import pandas as pd
import tempfile
import requests
import tarfile
import gzip
import csv
import os

from pandas.testing import assert_frame_equal

from io import BytesIO
from pathlib import Path

from zipfile import ZipFile
from unittest.mock import patch
from geopandas import GeoDataFrame

import urllib.request
import json

from pyro_risks import config as cfg
from pyro_risks.datasets import (
    masks,
    weather,
    wildfires,
    utils,
    nasa_wildfires,
    fwi,
    ERA5,
)
from pyro_risks.datasets.datasets_mergers import (
    merge_datasets_by_departements,
    merge_datasets_by_closest_weather_station,
    merge_datasets_by_closest_weather_point,
)


class UtilsTester(unittest.TestCase):
    def _test_get_intersection_range(self, s1, s2, expected_len):
        date_range = utils.get_intersection_range(s1, s2)
        self.assertIsInstance(date_range, pd.DatetimeIndex)
        self.assertEqual(len(date_range), expected_len)

    # Template unittest
    def test_get_intersection_range(self):
        # Non-intersecting series
        s1 = pd.Series(pd.date_range("2020-01-01", "2020-08-31"))
        s2 = pd.Series(pd.date_range("2020-09-01", "2020-11-01"))
        self.assertRaises(ValueError, utils.get_intersection_range, s1, s2)

        # s2 included in s1
        s1 = pd.Series(pd.date_range("2020-01-01", "2020-12-31"))
        s2 = pd.Series(pd.date_range("2020-09-01", "2020-09-30"))
        self._test_get_intersection_range(s1, s2, 30)

        # s2 included in s1
        s1 = pd.Series(pd.date_range("2020-09-01", "2020-11-01"))
        s2 = pd.Series(pd.date_range("2020-10-01", "2020-12-01"))
        self._test_get_intersection_range(s1, s2, 32)

    def test_load_data(self):
        with tempfile.TemporaryDirectory() as destination:
            fwi.load_data(output_path=destination)
            self.assertTrue(
                Path(destination, "fwi_unzipped/JRC_FWI_20190101.nc").is_file()
            )

    def test_get_fwi_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            fwi.load_data(output_path=tmp)
            df = fwi.get_fwi_data(source_path=tmp)
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(df.shape, (26538, 11))

    def test_create_departement_df(self):
        test_data = pd.DataFrame(
            {
                "latitude": {
                    0: 47.978,
                    1: 46.783,
                    2: 43.760,
                },
                "longitude": {
                    0: 5.132,
                    1: 4.710,
                    2: 1.335,
                },
                "fwi": {0: 6.7, 1: 0.3, 2: 8.9},
            }
        )
        res = fwi.create_departement_df(day_data=test_data)
        true_res = pd.DataFrame(
            {
                "latitude": {0: 47.978, 1: 46.783, 2: 43.76},
                "longitude": {0: 5.132, 1: 4.71, 2: 1.335},
                "departement": {
                    0: "Haute-Marne",
                    1: "Saône-et-Loire",
                    2: "Haute-Garonne",
                },
            }
        )
        assert_frame_equal(res, true_res)

    def test_include_departement(self):
        test_row = pd.Series({"latitude": 51.072, "longitude": 2.531, "fwi": 0.0})
        with urllib.request.urlopen(cfg.FR_GEOJSON) as url:
            dep_polygons = json.loads(url.read().decode())
        self.assertEqual(fwi.include_department(test_row, dep_polygons), "Nord")

    @patch("pyro_risks.datasets.utils.requests.get")
    def test_url_retrieve(self, mock_get):

        mock_get.return_value.status_code = 200
        mock_get.return_value.content = bytes("WEATHER OR WILDFIRE FILE", "utf-8")
        content = utils.url_retrieve("url")
        self.assertIsInstance(content, bytes)

        mock_get.return_value.status_code = 400
        mock_get.return_value.content = bytes("WEATHER OR WILDFIRE FILE", "utf-8")
        self.assertRaises(
            requests.exceptions.ConnectionError, utils.url_retrieve, "url"
        )

    def test_get_fname(self):

        url_firms = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/MODIS_C6_Europe_24h.csv"
        url_ghcn = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/2020.csv.gz"
        url_isd = "https://www.ncei.noaa.gov/data/global-hourly/archive/csv/2020.tar.gz"

        self.assertEqual(
            utils.get_fname(url_firms), ("MODIS_C6_Europe_24h", "csv", None)
        )
        self.assertEqual(utils.get_fname(url_ghcn), ("2020", "csv", "gz"))
        self.assertEqual(utils.get_fname(url_isd), ("2020", None, "tar.gz"))

    @staticmethod
    def _mock_csv(destination, fname):
        unzipped_content = [
            ["col1", "col2", "col3", "col4"],
            ["test", "test", "test", "test"],
            ["test", "test", "test", "test"],
            ["test", "test", "test", "test"],
        ]

        full_path = os.path.join(destination, "server/")

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(os.path.join(full_path, fname), mode="w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(unzipped_content)

    def _make_tarfile(self, destination):

        self._mock_csv(destination, "test_tar.csv")

        full_path = os.path.join(destination, "server/")
        out = tarfile.open(os.path.join(full_path, "test.tar.gz"), "w:gz")
        out.add(full_path, arcname=os.path.basename(full_path))
        out.close()

        with open(os.path.join(full_path, "test.tar.gz"), "rb") as tar_file:
            memory_file = BytesIO(tar_file.read())

        return memory_file

    def _make_gzipfile(self, destination):

        self._mock_csv(destination, "test_gz.csv")

        full_path = os.path.join(destination, "server/")
        with gzip.GzipFile(os.path.join(full_path, "test.gz"), mode="w") as gz, open(
            os.path.join(full_path, "test_gz.csv"), mode="r"
        ) as csvfile:
            gz.write(csvfile.read().encode())
            gz.close()

        with open(os.path.join(full_path, "test.gz"), "rb") as gz_file:
            memory_file = BytesIO(gz_file.read())

        return memory_file

    def _make_zipfile(self, destination):

        self._mock_csv(destination, "test_zip.csv")

        full_path = os.path.join(destination, "server/")
        with ZipFile(os.path.join(full_path, "test.zip"), "w") as zip_file:
            zip_file.write(
                os.path.join(full_path, "test_zip.csv"),
                os.path.basename(os.path.join(full_path, "test_zip.csv")),
            )

        with open(os.path.join(full_path, "test.zip"), "rb") as zip_file:
            memory_file = BytesIO(zip_file.read())

        return memory_file

    def _make_csv(self, destination):

        self._mock_csv(destination, "test_csv.csv")

        full_path = os.path.join(destination, "server/")
        with open(os.path.join(full_path, "test_csv.csv"), "rb") as csv_file:
            memory_file = BytesIO(csv_file.read())

        return memory_file

    @staticmethod
    def _mock_fname(compression):

        if compression == "tar.gz":
            return ("test_tar", "csv", "tar.gz")

        elif compression == "zip":
            return ("test_zip", "csv", "zip")

        elif compression == "csv":
            return ("test_csv", "csv", None)

        else:
            return ("test_gz", "csv", "gz")

    @patch("pyro_risks.datasets.utils.get_fname")
    @patch("pyro_risks.datasets.utils.url_retrieve")
    def test_download(self, mock_url_retrieve, mock_fname):
        with tempfile.TemporaryDirectory() as destination:

            full_path = os.path.join(destination, "client/")

            mock_fname.return_value = self._mock_fname("tar.gz")
            mock_url_retrieve.return_value = self._make_tarfile(destination).read()
            utils.download(url="url", default_extension="csv", destination=full_path)
            self.assertTrue(Path(full_path, "test_tar.csv").is_file())

            mock_fname.return_value = self._mock_fname("zip")
            mock_url_retrieve.return_value = self._make_zipfile(destination).read()
            utils.download(url="url", default_extension="csv", destination=full_path)
            self.assertTrue(Path(full_path, "test_zip.csv").is_file())

            mock_fname.return_value = self._mock_fname("gz")
            mock_url_retrieve.return_value = self._make_gzipfile(destination).read()
            utils.download(url="url", default_extension="csv", destination=full_path)
            self.assertTrue(Path(full_path, "test_gz.csv").is_file())

            mock_fname.return_value = self._mock_fname("csv")
            mock_url_retrieve.return_value = self._make_csv(destination).read()
            utils.download(
                url="url", default_extension="csv", unzip=False, destination=full_path
            )
            self.assertTrue(Path(full_path, "test_csv.csv").is_file())

            mock_fname.return_value = self._mock_fname("gz")
            mock_url_retrieve.return_value = self._make_gzipfile(destination).read()
            utils.download(
                url="url", default_extension="csv", unzip=False, destination=full_path
            )
            self.assertTrue(Path(full_path, "test_gz.gz").is_file())

            mock_fname.return_value = self._mock_fname("csv")
            self.assertRaises(ValueError, utils.download, "url", "csv", True, full_path)
            # utils.download(url='url', default_extension="csv", unzip=False, destination=full_path)

    def test_get_modis(self):
        with tempfile.TemporaryDirectory() as destination:
            utils.get_modis(
                start_year=2000, end_year=2001, yearly=True, destination=destination
            )
            utils.get_modis(destination=destination)
            self.assertTrue(Path(destination, "modis_2000_France.csv").is_file())
            self.assertTrue(Path(destination, "MODIS_C6_Europe_24h.csv").is_file())

    def test_get_ghcn(self):
        with tempfile.TemporaryDirectory() as destination:
            utils.get_ghcn(start_year=2000, end_year=2001, destination=destination)
            self.assertTrue(Path(destination, "2000.csv").is_file())

    def test_find_closest_weather_station(self):
        # Dataframe without STATION column
        df = pd.DataFrame(
            np.array([[5.876, 23.875], [8.986, 12.978]]),
            columns=["LATITUDE", "LONGITUDE"],
        )
        self.assertRaises(
            ValueError, utils.find_closest_weather_station, df, 3.871, 11.234
        )

        # Dataframe with STATION column
        df = pd.DataFrame(
            np.array(
                [
                    [5676499, 5.876, 23.875],
                    [4597821, 3.286, 12.978],
                    [8767822, 8.564, 10.764],
                ]
            ),
            columns=["STATION", "LATITUDE", "LONGITUDE"],
        )
        ref_station = utils.find_closest_weather_station(df, 3.871, 11.234)
        self.assertIsInstance(ref_station, int)

    def test_merge_datasets_by_departements(self):
        df_weather = weather.NOAAWeather()
        df_fires = wildfires.BDIFFHistory()
        df = merge_datasets_by_departements(
            df_weather, "DATE", "code", df_fires, "date", "Département", "left"
        )
        self.assertIsInstance(df, pd.DataFrame)

    def test_merge_datasets_by_closest_weather_station(self):
        df_weather = weather.NOAAWeather()
        nasa_firms = nasa_wildfires.NASAFIRMS()
        df = merge_datasets_by_closest_weather_station(
            df_weather, "DATE", nasa_firms, "acq_date"
        )
        self.assertIsInstance(df, pd.DataFrame)

    def test_merge_datasets_by_closest_weather_point(self):
        df_weather = ERA5.ERA5Land()
        nasa_firms = nasa_wildfires.NASAFIRMS()
        # take only a subset of the ERA5Land dataset because it is huge
        df_weather = df_weather[100:300]
        nasa_firms = nasa_firms[0:200]
        df = merge_datasets_by_closest_weather_point(
            df_weather, "time", nasa_firms, "acq_date"
        )
        self.assertIsInstance(df, pd.DataFrame)


class DatasetsTester(unittest.TestCase):
    def test_get_french_geom(self):
        fr_geom = masks.get_french_geom()
        self.assertIsInstance(fr_geom, GeoDataFrame)
        self.assertTrue(
            all(
                v1 == v2 for v1, v2 in zip(fr_geom.columns, ["code", "nom", "geometry"])
            )
        )

    def test_noaaweather(self):
        ds = weather.NOAAWeather()
        self.assertIsInstance(ds, pd.DataFrame)

    def test_bdiffhistory(self):
        ds = wildfires.BDIFFHistory()
        self.assertIsInstance(ds, pd.DataFrame)

    def test_nasafirms(self):
        ds = nasa_wildfires.NASAFIRMS()
        self.assertIsInstance(ds, pd.DataFrame)

    def test_gwisfwi(self):
        ds = fwi.GwisFwi()
        self.assertIsInstance(ds, pd.DataFrame)

    # def test_era5land(self):
    #     ds = ERA5.ERA5Land()
    #     self.assertIsInstance(ds, pd.DataFrame)


if __name__ == "__main__":
    unittest.main()
