from pyro_risks.datasets import NASAFIRMS_VIIRS, ERA5Land
from pyro_risks.datasets.utils import get_intersection_range
from pyro_risks.datasets.fwi import GwisFwi

import pandas as pd

__all__ = ["MergedEraFwiViirs"]


class MergedEraFwiViirs(pd.DataFrame):
    """Create dataframe for modeling described in models/score_v0.py.

    Get weather, nasafirms viirs fires and fwi datasets, then filter some of the lines corresponding
    to vegetation fires excluding low confidence ones merges. Finally aggregated versions of the
    dataframes by department and by day.
    For each of the features of weather and fwi datasets creates min, max, mean and std.
    Fires are counted for each department and day.

    Returns:
        pd.DataFrame
    """

    def __init__(self, era_source_path=None, viirs_source_path=None, fwi_source_path=None):
        """Define the merged era-fwi-viirs dataframe.

        Args:
            era_source_path (str, optional): Era5 data source path. Defaults to None.
            viirs_source_path (str, optional): Viirs data source path. Defaults to None.
            fwi_source_path (str, optional): Fwi data source path. Defaults to None.
        """
        weather = ERA5Land(era_source_path)
        nasa_firms = NASAFIRMS_VIIRS(viirs_source_path)

        # Time span selection
        date_range = get_intersection_range(weather.time, nasa_firms.acq_date)
        weather = weather[weather.time.isin(date_range)]
        nasa_firms = nasa_firms[nasa_firms.acq_date.isin(date_range)]

        # Keep only vegetation wildfires and remove thermal anomalies with low confidence
        where = (nasa_firms["confidence"] != "l") & (nasa_firms["type"] == 0)
        nasa_firms = nasa_firms[where]

        # Get FWI dataset for year 2019 (1st september missing)
        if fwi_source_path is None:
            days = [x.strftime("%Y%m%d") for x in pd.date_range(start="2019-01-01", end="2019-12-31")]
            days.remove('20190901')
            fwi_df = GwisFwi(days_list=days)
        else:
            fwi_df = pd.read_csv(fwi_source_path)

        # Load FWI dataset
        fwi_df["day"] = pd.to_datetime(fwi_df["day"], format="%Y%m%d", errors="coerce")

        # Group fwi dataframe by day and department and compute min, max, mean, std
        agg_fwi_df = fwi_df.groupby(['day', 'departement'])[
            'fwi', 'ffmc', 'dmc', 'dc', 'isi', 'bui', 'dsr'
        ].agg(['min', 'max', 'mean', 'std']).reset_index()
        agg_fwi_df.columns = ['day', 'departement'] + \
            [x[0] + '_' + x[1] for x in agg_fwi_df.columns if x[1] != '']

        # Group weather dataframe by day and department and compute min, max, mean, std
        agg_wth_df = weather.groupby(['time', 'nom'])[
            'u10', 'v10', 'd2m', 't2m', 'fal', 'lai_hv', 'lai_lv', 'skt',
            'asn', 'snowc', 'rsn', 'sde', 'sd', 'sf', 'smlt', 'stl1', 'stl2',
            'stl3', 'stl4', 'slhf', 'ssr', 'str', 'sp', 'sshf', 'ssrd', 'strd', 'tsn', 'tp'
        ].agg(['min', 'max', 'mean', 'std']).reset_index()
        agg_wth_df.columns = ['day', 'departement'] + \
            [x[0] + '_' + x[1] for x in agg_wth_df.columns if x[1] != '']

        # Merge fwi and weather together
        mid_df = pd.merge(agg_fwi_df, agg_wth_df,
                          on=['day', 'departement'],
                          how='inner')

        # Count fires by day and department
        fires_count = nasa_firms.groupby(
            ['acq_date', 'nom'])['confidence'].count().to_frame().reset_index()
        fires_count = fires_count.rename({'confidence': 'fires'}, axis=1)

        # Merge fires
        final_df = pd.merge(mid_df, fires_count,
                            left_on=['day', 'departement'],
                            right_on=['acq_date', 'nom'],
                            how='left').drop(['acq_date', 'nom'], axis=1)

        # Fill lines with no fires with 0
        final_df['fires'] = final_df['fires'].fillna(0)
        super().__init__(final_df)
