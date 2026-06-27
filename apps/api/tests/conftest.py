"""Shared pytest configuration.

Unit and lightweight API tests run in the testing environment and must not
require PostgreSQL unless a test explicitly opts into database connectivity.
"""

import os
from collections.abc import Iterator

import pytest
from app.config.settings import get_settings

TEST_ENVIRONMENT = {
    "APP_ENV": "testing",
    "DATABASE_CHECK_ON_STARTUP": "false",
    "SUPABASE_URL": "https://test-project.supabase.co",
    "SUPABASE_ANON_KEY": "test-anon-key",
    "SUPABASE_SERVICE_ROLE_KEY": "test-service-role-key",
    "SUPABASE_JWT_SECRET": "test-jwt-secret-with-32-bytes-minimum",
}


@pytest.fixture(autouse=True)
def configure_testing_environment() -> Iterator[None]:
    """Force lightweight tests to use deterministic testing settings."""

    previous_values = {key: os.environ.get(key) for key in TEST_ENVIRONMENT}
    os.environ.update(TEST_ENVIRONMENT)
    get_settings.cache_clear()
    try:
        yield
    finally:
        for key, previous_value in previous_values.items():
            if previous_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = previous_value
        get_settings.cache_clear()

