from pyro_risks.datasets import NASAFIRMS_VIIRS, ERA5Land
from pyro_risks.datasets.datasets_mergers import (
    merge_datasets_by_departements,
    merge_datasets_by_closest_weather_point,
    merge_by_proximity,
)
from pyro_risks.datasets.utils import get_intersection_range


def main(args):
    weather = ERA5Land(args.ERA5)
    nasa_firms = NASAFIRMS_VIIRS(args.nasa_firms, args.nasa_firms_type)
    print(weather.shape)
    print(nasa_firms.shape)

    # Time span selection
    date_range = get_intersection_range(weather.time, nasa_firms.acq_date)
    weather = weather[weather.time.isin(date_range)]
    nasa_firms = nasa_firms[nasa_firms.acq_date.isin(date_range)]

    print(weather.shape)
    print(nasa_firms.shape)

    print(weather.columns.tolist())
    print(nasa_firms.columns.tolist())

    # Keep only vegetation wildfires and remove thermal anomalies with low confidence
    where = (nasa_firms["confidence"] != "l") & (nasa_firms["type"] == 0)
    nasa_firms = nasa_firms[where]

    # Merge
    if args.type_of_merged == "departements":
        # drop redundant columns with weather datasets
        nasa_firms = nasa_firms.drop(["nom"], axis=1)
        merged_data = merge_datasets_by_departements(
            weather, "time", "code", nasa_firms, "acq_date", "code", "left"
        )
        to_drop = [
            "acq_date",
            "latitude_y",
            "longitude_y",
            "bright_ti4",
            "confidence",
            "bright_ti5",
            "frp",
            "type",
            "acq_date_time",
        ]

    else:
        # drop redundant columns with weather datasets
        nasa_firms = nasa_firms.drop(["code", "nom"], axis=1)
        # merged_data = merge_datasets_by_closest_weather_point(
        #     weather, "time", nasa_firms, "acq_date"
        # )
        merged_data = merge_by_proximity(
            nasa_firms, "acq_date", weather, "time", "right"
        )
        to_drop = [
            "acq_date",
            "latitude_y",
            "longitude_y",
            "bright_ti4",
            "confidence",
            "bright_ti5",
            "frp",
            "type",
            "acq_date_time",
        ]

    final_data = merged_data.copy()
    where = merged_data["confidence"].isna()
    final_data.loc[~where, "Statut"] = 1
    final_data.loc[where, "Statut"] = 0
    final_data["Statut"] = final_data["Statut"].astype(int)

    # drop unnecessary columns
    final_data = final_data.drop(to_drop, axis=1)

    print(final_data)
    print(final_data.shape)
    print(final_data.columns.tolist())


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Pyronear wildfire history example based on NASA FIRMS and ERA5 Land",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--ERA5", default=None, type=str, help="path or URL of ERA5 Land source"
    )

    parser.add_argument(
        "--nasa_firms",
        default=None,
        type=str,
        help="path or URL of NASA FIRMS data source",
    )

    parser.add_argument(
        "--nasa_firms_type",
        default="csv",
        type=str,
        help="type of NASA FIRMS data source",
    )

    parser.add_argument(
        "--type_of_merged",
        default="proximity",
        type=str,
        help="type of merged between weather and fire datasets: either departements or proximity",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
