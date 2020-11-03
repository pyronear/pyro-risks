import unittest
import pandas as pd
from geopandas import GeoDataFrame
from pyronear_ds.datasets import masks, weather, wildfires, utils


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


if __name__ == '__main__':
    unittest.main()
