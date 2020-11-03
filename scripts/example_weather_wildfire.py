import pandas as pd

from pyronear_ds.datasets import NOAAWeather, BDIFFHistory
from pyronear_ds.datasets.utils import get_intersection_range


def main(args):

    weather = NOAAWeather(args.weather)
    history = BDIFFHistory(args.wildfire)

    # Time span selection
    date_range = get_intersection_range(weather.DATE, history.date)
    weather = weather[weather.DATE.isin(date_range)]
    history = history[history.date.isin(date_range)]

    # Merge
    df = pd.merge(weather, history, left_on=['DATE', 'code'], right_on=['date', 'Département'], how='left')

    # Label data
    df.Statut = 1 - df.Statut.isna().astype(int)

    print(df.head())


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Pyronear weather & wildfire history example',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--weather', default=None, type=str, help='path or URL of NOAA weather source')
    parser.add_argument('--wildfire', default=None, type=str, help='path or URL of BDIFF history source')

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
