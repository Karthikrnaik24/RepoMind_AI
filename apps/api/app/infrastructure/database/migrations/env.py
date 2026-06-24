"""Alembic migration environment.

This file connects Alembic to the application settings and SQLAlchemy metadata.
It intentionally has no ORM model imports yet because Sprint 2 Milestone 2.1
does not create models or migration revisions.
"""

from logging.config import fileConfig

from alembic import context
from app.config.settings import get_settings
from app.infrastructure.database.base import Base
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    """Read the database URL from validated application settings."""

    return get_settings().database_url


def run_migrations_offline() -> None:
    """Configure Alembic for offline SQL generation."""

    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Configure Alembic for online migrations using SQLAlchemy."""

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
