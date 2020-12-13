import os
import secrets


PROJECT_NAME: str = 'PyroRisk'
PROJECT_DESCRIPTION: str = 'Wildfire risk estimation'
VERSION: str = "0.1.0a0"
DEBUG: bool = os.environ.get('DEBUG', '') != 'False'
LOGO_URL: str = "https://pyronear.org/img/logo_letters.png"


SECRET_KEY: str = secrets.token_urlsafe(32)
if DEBUG:
    # To keep the same Auth at every app loading in debug mode and not having to redo the auth.
    debug_secret_key = "000000000000000000000000000000000000"
    SECRET_KEY = debug_secret_key
