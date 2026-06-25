"""Testing environment settings."""

from pydantic import SecretStr

from app.config.base import BaseAppSettings


class TestingSettings(BaseAppSettings):
    """Settings used by automated tests."""

    app_environment: str = "testing"
    database_url: str = "sqlite+pysqlite:///:memory:"
    database_check_on_startup: bool = False
    supabase_url: str = "https://test-project.supabase.co"
    supabase_anon_key: SecretStr = SecretStr("test-anon-key")
    supabase_service_role_key: SecretStr = SecretStr("test-service-role-key")
    supabase_jwt_secret: SecretStr = SecretStr("test-jwt-secret")  # noqa: S105
    log_level: str = "WARNING"
