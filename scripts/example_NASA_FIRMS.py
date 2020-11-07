from pyronear_ds.datasets import NASAFIRMS


def main(args):

    nasa_firms = NASAFIRMS(args.nasa_firms)
    print(nasa_firms)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Pyronear weather & wildfire history example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--nasa_firms",
        default=None,
        type=str,
        help="path or URL of NASA FIRMS data source",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
