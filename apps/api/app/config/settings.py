"""Settings factory with backwards-compatible imports."""

import os
from functools import lru_cache

from app.config.base import BaseAppSettings
from app.config.development import DevelopmentSettings
from app.config.production import ProductionSettings
from app.config.testing import TestingSettings

Settings = BaseAppSettings


@lru_cache
def get_settings() -> Settings:
    """Return cached settings for the active environment."""

    environment = os.getenv("APP_ENV", "development").lower()
    settings_by_environment: dict[str, type[Settings]] = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "testing": TestingSettings,
    }
    return settings_by_environment.get(environment, DevelopmentSettings)()
