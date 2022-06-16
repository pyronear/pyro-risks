# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

# type: ignore
from pyro_risks.datasets.utils import download
from pyro_risks.pipeline import load_dataset, train_pipeline, evaluate_pipeline
from pyro_risks.pipeline import PyroRisk
from datetime import date

import pyro_risks.config as cfg
import click


@click.group()
def main():
    pass


@main.group(name="download")
def download_main():
    pass


@download_main.command(name="dataset")
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
def _download_dataset(url: str, default_extension: str, unzip: bool, destination: str):
    click.echo(f"Download {cfg.DATASET} dataset in {destination}")
    download(
        url=url,
        default_extension=default_extension,
        unzip=unzip,
        destination=destination,
    )


@download_main.command(name="inputs")
@click.option("--day", help="Date of interest (%Y-%m-%d) for example 2020-05-05")
@click.option("--country", default="France", help="Country of interest")
@click.option(
    "--directory", default=cfg.PREDICTIONS_REGISTRY, help="Dataset registry local path"
)
def _download_inputs(day: str, country: str, directory: str):
    day = day if day is not None else date.today().strftime("%Y-%m-%d")
    pyrorisk = PyroRisk()
    location = "default directory" if directory is None else directory
    click.echo(f"Download inputs in {location} to fire risks in {country} on {day}")
    pyrorisk.get_inputs(day=day, country=country, dir_destination=directory)
    click.echo("The fire risks inputs are downloaded")


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
) -> None:
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
def _evaluate_pipeline(
    pipeline: str, threshold: str, prefix: str, destination: str
) -> None:
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


@main.command(name="predict")
@click.option(
    "--model",
    default="RF",
    help="trained pipeline from pyrorisks remote model default to RF",
)
@click.option("--day", help="Date of interest (%Y-%m-%d) for example 2020-05-05")
@click.option("--country", default="France", help="Country of interest")
@click.option("--zone", default=cfg.ZONE_VAR, help="Territorial unit variable")
@click.option(
    "--directory",
    default=cfg.PREDICTIONS_REGISTRY,
    help="Predictions registry local path",
)
def _predict(model: str, day: str, country: str, zone: str, directory: str):
    day = day if day is not None else date.today().strftime("%Y-%m-%d")
    pyrorisk = PyroRisk(model=model)
    click.echo(f"Start predictions with the trained {pyrorisk.model} pipeline")
    pyrorisk.predict(
        day=day, country=country, zone_column=zone, dir_destination=directory
    )
    click.echo(
        f"Predictions are persisted in {directory}{pyrorisk.model}_prediction_{country}_{day}.joblib"
    )


if __name__ == "__main__":
    main()
