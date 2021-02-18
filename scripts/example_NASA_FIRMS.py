# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from pyro_risks.datasets import NASAFIRMS, NOAAWeather
from pyro_risks.datasets.datasets_mergers import (
    merge_datasets_by_closest_weather_station,
    merge_datasets_by_departements,
)
from pyro_risks.datasets.utils import get_intersection_range


def main(args):
    weather = NOAAWeather(args.weather)
    nasa_firms = NASAFIRMS(args.nasa_firms, args.nasa_firms_type)
    print(weather.shape)
    print(nasa_firms.shape)

    # Time span selection
    date_range = get_intersection_range(weather.DATE, nasa_firms.acq_date)
    weather = weather[weather.DATE.isin(date_range)]
    nasa_firms = nasa_firms[nasa_firms.acq_date.isin(date_range)]

    print(weather.shape)
    print(nasa_firms.shape)

    # Merge
    if args.type_of_merged == "departements":
        # drop redundant columns with weather datasets
        nasa_firms = nasa_firms.drop(["nom"], axis=1)
        merged_data = merge_datasets_by_departements(
            weather, "DATE", "code", nasa_firms, "acq_date", "code", "left"
        )
        to_drop = [
            # 'closest_weather_station',
            "acq_date",
            "latitude",
            "longitude",
            "bright_t31",
            "frp",
            "acq_date_time",
            "confidence",
        ]

    else:
        # drop redundant columns with weather datasets
        nasa_firms = nasa_firms.drop(["code", "nom"], axis=1)
        merged_data = merge_datasets_by_closest_weather_station(
            weather, "DATE", nasa_firms, "acq_date"
        )
        to_drop = [
            "closest_weather_station",
            "acq_date",
            "latitude",
            "longitude",
            "bright_t31",
            "frp",
            "acq_date_time",
            "confidence",
        ]

    final_data = merged_data.copy()
    where = merged_data["confidence"] >= 60
    final_data.loc[where, "Statut"] = 1
    final_data.loc[~where, "Statut"] = 0
    final_data["Statut"] = final_data["Statut"].astype(int)

    # drop unnecessary columns
    final_data = final_data.drop(to_drop, axis=1)

    print(final_data)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Pyronear wildfire history example based on NASA FIRMS",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--weather", default=None, type=str, help="path or URL of NOAA weather source"
    )

    parser.add_argument(
        "--nasa_firms",
        default=None,
        type=str,
        help="path or URL of NASA FIRMS data source",
    )

    parser.add_argument(
        "--nasa_firms_type",
        default="json",
        type=str,
        help="type of NASA FIRMS data source",
    )

    parser.add_argument(
        "--type_of_merged",
        default="departements",
        type=str,
        help="type of merged between weather and fire datasets: either departements or proximity",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
