from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_development(self) -> bool:
        return self.app_environment == "development"

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [self.frontend_origin]

    @model_validator(mode="after")
    def validate_production_cors(self) -> "Settings":
        if not self.is_development and self.frontend_origin == "*":
            msg = "FRONTEND_ORIGIN cannot be a wildcard outside development."
            raise ValueError(msg)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
