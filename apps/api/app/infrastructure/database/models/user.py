"""User and profile ORM models.

These models map only the `users` and `user_profiles` tables from
docs/DATABASE.md. They intentionally contain no authentication or CRUD logic.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel, SoftDeleteBaseModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.indexing import IndexingJob
    from app.infrastructure.database.models.repository import Repository


class User(SoftDeleteBaseModel):
    """Authenticated user account and identity-provider linkage."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'suspended', 'deleted')",
            name="status_valid",
        ),
        Index(
            "uq_users_email_active",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "uq_users_auth_provider_auth_provider_user_id",
            "auth_provider",
            "auth_provider_user_id",
            unique=True,
        ),
        Index("ix_users_status", "status"),
        Index("ix_users_created_at", "created_at"),
    )

    email: Mapped[str] = mapped_column(String(320), nullable=False)
    auth_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    auth_provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)

    profile: Mapped["UserProfile | None"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        single_parent=True,
        uselist=False,
    )
    repositories: Mapped[list["Repository"]] = relationship(
        back_populates="owner",
        passive_deletes=True,
    )
    requested_indexing_jobs: Mapped[list["IndexingJob"]] = relationship(
        back_populates="requested_by",
        passive_deletes=True,
    )


class UserProfile(BaseModel):
    """User-facing profile metadata separated from authentication identity."""

    __tablename__ = "user_profiles"
    __table_args__ = (
        Index("ix_user_profiles_display_name", "display_name"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    locale: Mapped[str | None] = mapped_column(String(20), nullable=True)

    user: Mapped[User] = relationship(back_populates="profile")
