"""Base environment-driven settings.

All environment-specific settings inherit from this module so infrastructure,
API routes, and dependency providers share one typed configuration contract.
"""

from pydantic import Field, model_validator
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
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    frontend_origin: str = Field(default="http://localhost:3000", alias="FRONTEND_ORIGIN")
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

    @model_validator(mode="after")
    def validate_production_cors(self) -> "BaseAppSettings":
        """Prevent wildcard browser access outside local development."""

        if not self.is_development and self.frontend_origin == "*":
            msg = "FRONTEND_ORIGIN cannot be a wildcard outside development."
            raise ValueError(msg)
        return self
