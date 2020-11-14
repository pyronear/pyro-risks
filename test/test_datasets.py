import unittest
import pandas as pd
from geopandas import GeoDataFrame
import urllib.request

from pathlib import Path
import tempfile
import json

from pyronear_ds import config as cfg
from pyronear_ds.datasets import masks, weather, wildfires, utils, nasa_wildfires, fwi


class UtilsTester(unittest.TestCase):

    def _test_get_intersection_range(self, s1, s2, expected_len):
        date_range = utils.get_intersection_range(s1, s2)
        self.assertIsInstance(date_range, pd.DatetimeIndex)
        self.assertEqual(len(date_range), expected_len)

    # Template unittest
    def test_get_intersection_range(self):

        # Non-intersecting series
        s1 = pd.Series(pd.date_range('2020-01-01', '2020-08-31'))
        s2 = pd.Series(pd.date_range('2020-09-01', '2020-11-01'))
        self.assertRaises(ValueError, utils.get_intersection_range, s1, s2)

        # s2 included in s1
        s1 = pd.Series(pd.date_range('2020-01-01', '2020-12-31'))
        s2 = pd.Series(pd.date_range('2020-09-01', '2020-09-30'))
        self._test_get_intersection_range(s1, s2, 30)

        # s2 included in s1
        s1 = pd.Series(pd.date_range('2020-09-01', '2020-11-01'))
        s2 = pd.Series(pd.date_range('2020-10-01', '2020-12-01'))
        self._test_get_intersection_range(s1, s2, 32)

    def test_load_data(self):
        with tempfile.TemporaryDirectory() as destination:
            fwi.load_data(output_path=destination)
            self.assertTrue(Path(destination, 'fwi_unzipped/JRC_FWI_20190101.nc').is_file())

    def test_fwi_day_data(self):
        df = fwi.get_fwi_data()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (26538, 11))

    def test_create_departement_df(self):
        with tempfile.TemporaryDirectory() as destination:
            test_data = pd.DataFrame({'latitude': {0: 47.97890853881836,
                                                   1: 46.78382873535156,
                                                   2: 43.760982513427734,
                                                   },
                                      'longitude': {0: 5.1328125,
                                                    1: 4.7109375,
                                                    2: 1.3359375,
                                                    },
                                      'fwi': {0: 6.7, 1: 0.3, 2: 8.9}})
            fwi.create_departement_df(day_data=test_data, output_path=destination)
            self.assertTrue(Path(destination, 'departement_df.pickle').is_file())

    def test_include_departement(self):
        test_row = pd.Series({"latitude": 51.072, "longitude": 2.531, "fwi": 0.0})
        with urllib.request.urlopen(cfg.FR_GEOJSON) as url:
            dep_polygons = json.loads(url.read().decode())
        self.assertEqual(fwi.include_department(test_row, dep_polygons), 'Nord')


class DatasetsTester(unittest.TestCase):

    def test_get_french_geom(self):
        fr_geom = masks.get_french_geom()
        self.assertIsInstance(fr_geom, GeoDataFrame)
        self.assertTrue(all(v1 == v2 for v1, v2 in zip(fr_geom.columns, ['code', 'nom', 'geometry'])))

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


if __name__ == '__main__':
    unittest.main()
