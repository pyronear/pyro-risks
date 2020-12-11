import os

FR_GEOJSON: str = "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
DATA_FALLBACK: str = (
    "https://github.com/pyronear/pyro-risks/releases/download/v0.1.0-data"
)
FR_GEOJSON_FALLBACK: str = f"{DATA_FALLBACK}/departements.geojson"
FR_FIRES_FALLBACK: str = f"{DATA_FALLBACK}/export_BDIFF_incendies_20201027.csv"
FR_WEATHER_FALLBACK: str = f"{DATA_FALLBACK}/noaa_weather_20201025.csv"
FR_NASA_FIRMS_FALLBACK: str = f"{DATA_FALLBACK}/NASA_FIRMS.json"
FR_NASA_VIIRS_FALLBACK: str = f"{DATA_FALLBACK}/NASA_FIRMS_VIIRS_2018_2020.csv"
FR_FWI_2019_FALLBACK: str = f"{DATA_FALLBACK}/JRC_FWI_2019.zip"
FR_FWI_2020_FALLBACK: str = f"{DATA_FALLBACK}/JRC_FWI_2020.zip"
FR_ERA5LAND_FALLBACK: str = f"{DATA_FALLBACK}/ERA5_2019.nc"
FR_ERA5T_FALLBACK: str = f"{DATA_FALLBACK}/era5t_2019.nc"
TEST_FR_ERA5LAND_FALLBACK: str = f"{DATA_FALLBACK}/test_data_ERA5_2018.nc"
TEST_FR_FIRMS_CSV_FALLBACK: str = f"{DATA_FALLBACK}/test_data_FIRMS.csv"
TEST_FR_FIRMS_XLSX_FALLBACK: str = f"{DATA_FALLBACK}/test_data_FIRMS.xlsx"
TEST_FR_VIIRS_XLSX_FALLBACK: str = f"{DATA_FALLBACK}/test_data_VIIRS.xlsx"
TEST_FR_VIIRS_JSON_FALLBACK: str = f"{DATA_FALLBACK}/test_data_VIIRS.json"
TEST_FR_ERA5_2019_FALLBACK: str = f"{DATA_FALLBACK}/test_data_ERA5_2019.nc"
TEST_FWI_FALLBACK: str = f"{DATA_FALLBACK}/test_data_FWI.csv"

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(REPO_DIR, ".data/")

RFMODEL_PATH: str = f"{DATA_FALLBACK}/pyrorisk_rfc_111220.pkl"
XGBMODEL_PATH: str = f"{DATA_FALLBACK}/pyrorisk_xgb_091220.pkl"

MODEL_VARIABLES = ['ffmc_min', 'str_mean', 'str_min', 'str_max', 'ffmc_mean', 'isi_min',
                   'ffmc_min_lag1', 'strd_mean', 'isi_mean', 'strd_min', 'strd_max',
                   'rsn_max', 'ffmc_mean_lag1', 'rsn_max_lag1', 'str_mean_lag1',
                   'str_min_lag1', 'ffmc_std', 'ffmc_max', 'rsn_std', 'str_max_lag1',
                   'rsn_std_lag1', 'rsn_max_lag3', 'isi_min_lag1', 'isi_mean_lag1',
                   'ffmc_max_lag1', 'rsn_std_lag3', 'stl1_std_lag1', 'stl1_std', 'isi_max',
                   'strd_min_lag1', 'ffmc_min_lag3', 'ffmc_std_lag1', 'strd_mean_lag1',
                   'rsn_mean_lag1', 'fwi_mean', 'isi_max_lag1', 'sd_max', 'strd_max_lag1',
                   'rsn_mean', 'snowc_std_lag7', 'stl1_std_lag3']
TRAIN_SELECTED_DEP = ['Aisne', 'Alpes-Maritimes', 'Ardèche', 'Ariège', 'Aude', 'Aveyron',
                      'Cantal', 'Eure', 'Eure-et-Loir', 'Gironde', 'Haute-Corse', 'Hautes-Pyrénées',
                      'Hérault', 'Indre', 'Landes', 'Loiret', 'Lozère', 'Marne', 'Oise',
                      'Pyrénées-Atlantiques', 'Pyrénées-Orientales', 'Sarthe', 'Somme', 'Yonne']

RF_PARAMS = {
    "n_estimators": 500,
    "min_samples_leaf": 10,
    "max_features": 'sqrt',
    "class_weight": "balanced",
    "criterion": 'gini',
    "random_state": 10,
    "n_jobs": -1
}

XGB_PARAMS = {
    'max_depth': 10,
    'min_child_weight': 10,
    'eta': .01,
    'subsample': .8,
    'colsample_bytree': .8,
    'objective': 'binary:logistic',
    'eval_metric': ['logloss', 'aucpr']
}
