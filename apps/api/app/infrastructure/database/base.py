"""SQLAlchemy declarative base for future ORM models.

No ORM models are defined during Sprint 2 Milestone 2.1. This metadata object
exists so Alembic and future model modules have a single source of truth.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class all future SQLAlchemy ORM models must inherit from."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
