"""Production environment settings."""

from app.config.base import BaseAppSettings


class ProductionSettings(BaseAppSettings):
    """Settings optimized for production safety."""

    app_environment: str = "production"
    log_level: str = "INFO"
    log_json: bool = True
