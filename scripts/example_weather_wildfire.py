from pyro_risks.datasets import NOAAWeather, BDIFFHistory
from pyro_risks.datasets.datasets_mergers import merge_datasets_by_departements
from pyro_risks.datasets.utils import get_intersection_range


def main(args):
    weather = NOAAWeather(args.weather)
    history = BDIFFHistory(args.wildfire)

    # Time span selection
    date_range = get_intersection_range(weather.DATE, history.date)
    weather = weather[weather.DATE.isin(date_range)]
    history = history[history.date.isin(date_range)]

    # Merge
    df = merge_datasets_by_departements(
        weather, "DATE", "code", history, "date", "Département", "left"
    )

    # Label data
    df.Statut = 1 - df.Statut.isna().astype(int)

    df = df.filter(
        items=[
            "DATE",
            "code",
            "nom",
            "LATITUDE",
            "LONGITUDE",
            "ELEVATION",
            "DEWP",
            "DEWP_ATTRIBUTES",
            "FRSHTT",
            "GUST",
            "MAX",
            "MIN",
            "MXSPD",
            "PRCP",
            "SLP",
            "SLP_ATTRIBUTES",
            "SNDP",
            "STP",
            "STP_ATTRIBUTES",
            "TEMP",
            "TEMP_ATTRIBUTES",
            "VISIB",
            "VISIB_ATTRIBUTES",
            "WDSP",
            "WDSP_ATTRIBUTES",
            "Statut",
        ]
    )

    print(df)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Pyronear weather & wildfire history example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--weather", default=None, type=str, help="path or URL of NOAA weather source"
    )
    parser.add_argument(
        "--wildfire", default=None, type=str, help="path or URL of BDIFF history source"
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
