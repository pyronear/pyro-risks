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
FR_ERA5LAND_FALLBACK: str = f"{DATA_FALLBACK}/ERA5_2018_2020.nc"
TEST_FR_ERA5LAND_FALLBACK: str = f"{DATA_FALLBACK}/test_data_ERA5_2018.nc"
TEST_FR_FIRMS_CSV_FALLBACK: str = f"{DATA_FALLBACK}/test_data_FIRMS.csv"
TEST_FR_FIRMS_XLSX_FALLBACK: str = f"{DATA_FALLBACK}/test_data_FIRMS.xlsx"
TEST_FR_VIIRS_XLSX_FALLBACK: str = f"{DATA_FALLBACK}/test_data_VIIRS.xlsx"
TEST_FR_VIIRS_JSON_FALLBACK: str = f"{DATA_FALLBACK}/test_data_VIIRS.json"
TEST_FR_ERA5_2019: str = f"{DATA_FALLBACK}/test_data_ERA5_2019.nc"
TEST_FWI_FALLBACK: str = f"{DATA_FALLBACK}/test_data_FWI.csv"

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(REPO_DIR, ".data/")
