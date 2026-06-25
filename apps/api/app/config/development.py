"""Development environment settings."""

from app.config.base import BaseAppSettings


class DevelopmentSettings(BaseAppSettings):
    """Settings optimized for local developer feedback."""

    app_environment: str = "development"
    log_level: str = "DEBUG"
