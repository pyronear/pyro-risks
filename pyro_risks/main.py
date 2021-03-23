# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from pyro_risks.datasets.utils import download
from pyro_risks.pipeline import load_dataset, train_pipeline, evaluate_pipeline

import pyro_risks.config as cfg
import click


@click.group()
def main():
    pass


@main.command(name="download")
@click.option("--url", default=cfg.ERA5T_VIIRS_PIPELINE, help="Dataset URL")
@click.option(
    "--extension", "default_extension", default="csv", help="Dataset file extension"
)
@click.option(
    "--unzip",
    is_flag=True,
    default=False,
    help="Wether the dataset file should be unzip or not",
)
@click.option(
    "--destination", default=cfg.DATA_REGISTRY, help="Dataset registry local path"
)
def _download(url: str, default_extension: str, unzip: bool, destination: str):
    click.echo(f"Download {cfg.DATASET} dataset in {destination}")
    download(
        url=url,
        default_extension=default_extension,
        unzip=unzip,
        destination=destination,
    )


@main.command(name="train")
@click.option("--model", help="Classification Pipeline name RF, XGBOOST")
@click.option(
    "--destination",
    default=cfg.MODEL_REGISTRY,
    help="Destination folder for persisting pipeline.",
)
@click.option(
    "--ignore_prints/--print", is_flag=True, help="Whether to print results or not."
)
@click.option(
    "--ignore_html/--html", is_flag=True, help="Persist pipeline html description."
)
def _train_pipeline(
    model: str, destination: str, ignore_prints: bool, ignore_html: bool
):
    click.echo(f"Train and save pipeline in {destination}")
    X, y = load_dataset()
    train_pipeline(
        X=X,
        y=y,
        model=model,
        destination=destination,
        ignore_prints=ignore_prints,
        ignore_html=ignore_html,
    )


@main.command(name="evaluate")
@click.option("--pipeline", help="Pipeline location path.")
@click.option("--threshold", help="Classification pipeline optimal threshold path.")
@click.option("--prefix", help="Classification reports prefix i.e. pipeline name.")
@click.option(
    "--destination",
    default=cfg.METADATA_REGISTRY,
    help="Folder where the report should be saved.",
)
def _evaluate_pipeline(pipeline: str, threshold: str, prefix: str, destination: str):
    click.echo(f"Evaluate and save pipeline performance metrics in {destination}")
    X, y = load_dataset()
    evaluate_pipeline(
        X=X,
        y=y,
        pipeline=pipeline,
        threshold=threshold,
        prefix=prefix,
        destination=destination,
    )


if __name__ == "__main__":
    main()
