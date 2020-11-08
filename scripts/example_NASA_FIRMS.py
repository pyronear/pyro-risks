from pyronear_ds.datasets import NASAFIRMS


def main(args):

    nasa_firms = NASAFIRMS(args.nasa_firms, args.nasa_firms_type)
    print(nasa_firms)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Pyronear wildfire history example based on NASA FIRMS",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--nasa_firms",
        default=None,
        type=str,
        help="path or URL of NASA FIRMS data source",
    )

    parser.add_argument(
        "--nasa_firms_type",
        default='json',
        type=str,
        help="type of NASA FIRMS data source",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
