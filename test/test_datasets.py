import unittest

import numpy as np
import pandas as pd
from geopandas import GeoDataFrame

from pyronear_ds.datasets import masks, weather, wildfires, utils, nasa_wildfires


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

    def test_find_closest_weather_station(self):
        # Dataframe without STATION column
        df = pd.DataFrame(np.array([[5.876, 23.875], [8.986, 12.978]]), columns=['LATITUDE', 'LONGITUDE'])
        self.assertRaises(ValueError, utils.find_closest_weather_station, df, 3.871, 11.234)

        # Dataframe with STATION column
        df = pd.DataFrame(np.array([[5676499, 5.876, 23.875], [4597821, 3.286, 12.978], [8767822, 8.564, 10.764]]),
                          columns=['STATION', 'LATITUDE', 'LONGITUDE'])
        ref_station = utils.find_closest_weather_station(df, 3.871, 11.234)
        self.assertIsInstance(ref_station, int)


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


if __name__ == '__main__':
    unittest.main()
