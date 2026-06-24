"""SQLAlchemy engine, session factory, and FastAPI session dependency.

This module centralizes database lifecycle management so API routes and future
application services do not create engines or sessions directly.
"""

from collections.abc import Generator

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import Settings, get_settings


def create_database_engine(settings: Settings | None = None) -> Engine:
    """Create a SQLAlchemy 2.x engine from validated application settings."""

    resolved_settings = settings or get_settings()
    return create_engine(
        resolved_settings.database_url,
        pool_pre_ping=True,
        pool_size=resolved_settings.database_pool_size,
        max_overflow=resolved_settings.database_max_overflow,
        pool_recycle=resolved_settings.database_pool_recycle_seconds,
    )


engine = create_database_engine()
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db_session() -> Generator[Session, None, None]:
    """Yield a request-scoped database session for FastAPI dependency injection."""

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_database_connection() -> None:
    """Verify database connectivity during application startup."""

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def close_database_connections() -> None:
    """Dispose pooled connections during graceful application shutdown."""

    engine.dispose()
