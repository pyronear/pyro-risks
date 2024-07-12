# Copyright (C) 2021-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

__all__ = ["settings"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="./../../.env")

    PROJECT_NAME: str = "Pyrorisks"
    PROJECT_DESCRIPTION: str = "API for wildfire risk estimation"
    LOGO_URL: str = "https://pyronear.org/img/logo_letters.png"
    VERSION: str = "0.1.0"
    DEBUG: bool

    @field_validator("DEBUG", mode="before")
    @classmethod
    def transform_debug(cls, value: str) -> bool:
        return value != "False"

    S3_BUCKET_NAME: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_REGION: str
    S3_ENDPOINT_URL: str


settings = Settings()
