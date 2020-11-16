import os

FR_GEOJSON: str = "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
DATA_FALLBACK: str = "https://github.com/pyronear/pyro-risks/releases/download/v0.1.0-data"
FR_GEOJSON_FALLBACK: str = f"{DATA_FALLBACK}/departements.geojson"
FR_FIRES_FALLBACK: str = f"{DATA_FALLBACK}/export_BDIFF_incendies_20201027.csv"
FR_WEATHER_FALLBACK: str = f"{DATA_FALLBACK}/noaa_weather_20201025.csv"
FR_NASA_FIRMS_FALLBACK: str = f"{DATA_FALLBACK}/NASA_FIRMS.json"
FR_FWI_2019_FALLBACK: str = f"{DATA_FALLBACK}/JRC_FWI_2019.zip"
FR_FWI_2020_FALLBACK: str = f"{DATA_FALLBACK}/JRC_FWI_2020.zip"

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(REPO_DIR, '.data/')
