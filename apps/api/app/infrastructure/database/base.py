"""Reusable SQLAlchemy declarative foundations.

This module defines only infrastructure primitives shared by future ORM models.
It intentionally does not define business models or database tables.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, MetaData, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Base(DeclarativeBase):
    """Declarative base class all future SQLAlchemy ORM models must inherit from."""

    metadata = metadata


class TableNameMixin:
    """Generate snake_case table names from class names when not set explicitly."""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        name = cls.__name__
        chars: list[str] = []
        for index, char in enumerate(name):
            if char.isupper() and index > 0:
                chars.append("_")
            chars.append(char.lower())
        return "".join(chars)


class UUIDPrimaryKeyMixin:
    """Provide a UUID primary key suitable for externally referenced entities."""

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
    )


class TimestampMixin:
    """Track record creation and update timestamps in UTC."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Provide nullable soft-delete metadata for auditable records."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    @property
    def is_deleted(self) -> bool:
        """Return whether this record has been soft deleted."""

        return self.deleted_at is not None

    def mark_deleted(self, deleted_at: datetime | None = None) -> None:
        """Mark this record as soft deleted without removing it from the database."""

        self.deleted_at = deleted_at or datetime.now(UTC)

    def restore(self) -> None:
        """Clear the soft-delete timestamp."""

        self.deleted_at = None


class ReprMixin:
    """Provide a compact debug representation for model instances."""

    def __repr__(self) -> str:
        identity = getattr(self, "id", None)
        return f"<{self.__class__.__name__}(id={identity})>"


class BaseModel(
    TableNameMixin,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    ReprMixin,
    Base,
):
    """Abstract base for future active records.

    Future ORM models can inherit from this class when they need the standard
    UUID primary key and timestamp columns.
    """

    __abstract__ = True


class SoftDeleteBaseModel(
    SoftDeleteMixin,
    BaseModel,
):
    """Abstract base for future records that support soft deletion."""

    __abstract__ = True


def model_to_dict(model: Any) -> dict[str, Any]:
    """Return mapped column values for simple diagnostics and tests."""

    return {column.key: getattr(model, column.key) for column in model.__table__.columns}
