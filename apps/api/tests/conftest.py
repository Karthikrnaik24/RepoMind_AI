"""Shared pytest configuration.

Unit and lightweight API tests run in the testing environment and must not
require PostgreSQL unless a test explicitly opts into database connectivity.
"""

import os
from collections.abc import Iterator

import pytest
from app.config.settings import get_settings


@pytest.fixture(autouse=True)
def configure_testing_environment() -> Iterator[None]:
    """Force lightweight tests to use testing settings."""

    previous_app_env = os.environ.get("APP_ENV")
    previous_startup_check = os.environ.get("DATABASE_CHECK_ON_STARTUP")
    os.environ["APP_ENV"] = "testing"
    os.environ.setdefault("DATABASE_CHECK_ON_STARTUP", "false")
    get_settings.cache_clear()
    try:
        yield
    finally:
        if previous_app_env is None:
            os.environ.pop("APP_ENV", None)
        else:
            os.environ["APP_ENV"] = previous_app_env
        if previous_startup_check is None:
            os.environ.pop("DATABASE_CHECK_ON_STARTUP", None)
        else:
            os.environ["DATABASE_CHECK_ON_STARTUP"] = previous_startup_check
        get_settings.cache_clear()
