"""Base environment-driven settings.

All environment-specific settings inherit from this module so infrastructure,
API routes, and dependency providers share one typed configuration contract.
"""

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAppSettings(BaseSettings):
    """Common settings used by every runtime environment."""

    app_name: str = "RepoMind AI API"
    app_version: str = "0.1.0"
    app_environment: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(
        default="postgresql+psycopg://repomind:repomind@localhost:5432/repomind",
        alias="DATABASE_URL",
    )
    database_pool_size: int = Field(default=5, alias="DATABASE_POOL_SIZE", ge=1)
    database_max_overflow: int = Field(default=10, alias="DATABASE_MAX_OVERFLOW", ge=0)
    database_pool_recycle_seconds: int = Field(
        default=1800,
        alias="DATABASE_POOL_RECYCLE_SECONDS",
        ge=1,
    )
    database_check_on_startup: bool = Field(default=True, alias="DATABASE_CHECK_ON_STARTUP")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    frontend_origin: str = Field(default="http://localhost:3000", alias="FRONTEND_ORIGIN")
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_jwks_url: str = Field(default="", alias="SUPABASE_JWKS_URL")
    supabase_anon_key: SecretStr = Field(default=SecretStr(""), alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: SecretStr = Field(
        default=SecretStr(""),
        alias="SUPABASE_SERVICE_ROLE_KEY",
    )
    supabase_jwt_secret: SecretStr = Field(default=SecretStr(""), alias="SUPABASE_JWT_SECRET")
    github_api_base_url: str = Field(default="https://api.github.com", alias="GITHUB_API_BASE_URL")
    github_api_timeout_seconds: float = Field(
        default=10.0,
        alias="GITHUB_API_TIMEOUT_SECONDS",
        gt=0,
    )
    github_api_max_retries: int = Field(default=2, alias="GITHUB_API_MAX_RETRIES", ge=0)
    github_api_retry_backoff_seconds: float = Field(
        default=0.25,
        alias="GITHUB_API_RETRY_BACKOFF_SECONDS",
        ge=0,
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=True, alias="LOG_JSON")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_development(self) -> bool:
        """Return whether the app is running in development mode."""

        return self.app_environment == "development"

    @property
    def is_production(self) -> bool:
        """Return whether the app is running in production mode."""

        return self.app_environment == "production"

    @property
    def cors_allowed_origins(self) -> list[str]:
        """Return CORS origins validated from environment configuration."""

        return [self.frontend_origin]

    @property
    def is_supabase_configured(self) -> bool:
        """Return whether required Supabase identity settings are present."""

        return all(
            [
                self.supabase_url,
                self.supabase_anon_key.get_secret_value(),
                self.supabase_service_role_key.get_secret_value(),
                self.supabase_jwks_url,

            ],
        )

    @model_validator(mode="after")
    def derive_supabase_jwks_url(self) -> "BaseAppSettings":
        """Derive the Supabase JWKS URL from SUPABASE_URL when omitted."""

        if self.supabase_url and not self.supabase_jwks_url:
            self.supabase_jwks_url = (
                f"{self.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
            )
        return self

    @model_validator(mode="after")
    def validate_production_cors(self) -> "BaseAppSettings":
        """Prevent wildcard browser access outside local development."""

        if not self.is_development and self.frontend_origin == "*":
            msg = "FRONTEND_ORIGIN cannot be a wildcard outside development."
            raise ValueError(msg)
        return self

