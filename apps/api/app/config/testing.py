"""Testing environment settings."""

from app.config.base import BaseAppSettings


class TestingSettings(BaseAppSettings):
    """Settings used by automated tests."""

    app_environment: str = "testing"
    database_url: str = "sqlite+pysqlite:///:memory:"
    log_level: str = "WARNING"
