import os

from sklearn.model_selection import StratifiedKFold

from pyronear_ds.models.pyronear_xgb_classifier import PyronearXGBoostClassifier
from pyronear_ds.models.xgb_classifier_pipeline import XGBClassifierPipeline
from pyronear_ds.preprocess.cleaner.columns_remover import ColumnsRemover
from pyronear_ds.preprocess.cleaner.convert_datetimes_cleaner import (
    ConvertDatetimesCleaner,
)
from pyronear_ds.preprocess.cleaner.datetime_splitter import DatetimeSplitter
from pyronear_ds.preprocess.cleaner.drop_na_cleaner import DropNaCleaner
from pyronear_ds.preprocess.data_provider.data_provider import DataProvider
from pyronear_ds.preprocess.final_merger.final_merger_departements import FinalMergerDepartement
from pyronear_ds.preprocess.final_merger.same_time_span_selector import (
    SameTimeSpanSelector,
)
from pyronear_ds.preprocess.geo_merger.geo_merger_fires import GeoMergerFires
from pyronear_ds.preprocess.geo_merger.geo_merger_weather import GeoMergerWeather
from pyronear_ds.preprocess.label_converter.classification_label_converter import ClassificationLabelConverter
from pyronear_ds.preprocess.preprocess_pipeline import PreprocessPipeline
from pyronear_ds.preprocess.reader.csv_reader import CsvReader
from pyronear_ds.preprocess.reader.geographic_reader import GeographicReader

datetime_format_weather = {
    "DATE": "%Y-%m-%d",
}

datetime_format_fires = {
    "Date": "%Y-%m-%d",
    "Heure": "%H:%M:%S",
    "Date de première alerte": "%Y-%m-%d %H:%M:%S",
}


def main():
    weather_data_provider = DataProvider(
        GeoMergerWeather(
            CsvReader(
                os.path.join(
                    os.path.dirname(__file__), "data/global_summary_of_day.csv"
                ),
                separator=",",
            ),
            GeographicReader(
                "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
            ),
            time_col="DATE",
            geometry_col="geometry",
        ),
        [
            DropNaCleaner(),
            ConvertDatetimesCleaner(datetime_format_weather),
            ColumnsRemover(["index_right"]),
            # MissingValuesCleaner()
        ],
    )

    fires_data_provider = DataProvider(
        GeoMergerFires(
            CsvReader(
                os.path.join(
                    os.path.dirname(__file__),
                    "data/export_BDIFF_incendies_20201027.csv",
                ),
                separator=";",
            ),
            GeographicReader(
                "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
            ),
            time_col="Date",
            geometry_col="DepartementGeometry",
        ),
        [
            DropNaCleaner(cols_to_except=["DepartementGeometry"]),
            DatetimeSplitter(),
            ConvertDatetimesCleaner(datetime_format_fires),
        ],
    )

    time_span_selector = SameTimeSpanSelector()

    final_merger = FinalMergerDepartement("left")

    cleaners = [
        ColumnsRemover(
            [
                "Heure",
                "DepartementGeometry",
                "Année",
                "STATION",
                "Numéro",
                "Département",
                "Code INSEE",
                "Date de première alerte",
                "Surface brûlée (m2)",
                "Surface forêt (m2)",
                "Surface autres terres boisées (m2)",
                "Surfaces non boisées (m2)",
                "Date",
                "PRCP_ATTRIBUTES",
                "NAME",
                "nom",
                "MAX_ATTRIBUTES",
                "MIN_ATTRIBUTES",
                "geometry",
                "code",
                "DATE",
            ]
        )
    ]

    label_converter = ClassificationLabelConverter("Statut")

    preprocess_pipeline = PreprocessPipeline(
        weather_data_provider,
        fires_data_provider,
        time_span_selector,
        final_merger,
        cleaners,
        label_converter
    )

    data = preprocess_pipeline.pipeline()

    xgb_params = {
        "objective": "binary:logistic",
        "learning_rate": 0.1,
        "min_child_weight": 4,
        "subsample": 0.5,
        "colsample_bytree": 0.6,
        "n_estimators": 1000,
        "n_jobs": -1,
    }

    cv = StratifiedKFold(n_splits=6)

    classifier = PyronearXGBoostClassifier(
        params=xgb_params, label_column="Statut", cross_validator=cv, scoring="recall",
    )

    scores, predictions = XGBClassifierPipeline(classifier=classifier).pipeline(
        data=data
    )

    return data, scores, predictions


if __name__ == "__main__":
    data, scores, predictions = main()
    print(data)
    print('Mean recall on cross-validation: ', scores.mean())
    print(predictions)
