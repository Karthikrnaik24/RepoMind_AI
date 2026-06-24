"""Repository and branch ORM models.

These models map only the `repositories` and `repository_branches` tables from
docs/DATABASE.md. They intentionally contain no repository business logic.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.user import User


class Repository(BaseModel):
    """Connected repository and provider metadata."""

    __tablename__ = "repositories"
    __table_args__ = (
        CheckConstraint(
            "visibility IN ('public', 'private', 'internal')",
            name="visibility_valid",
        ),
        Index(
            "uq_repositories_provider_provider_repository_id",
            "provider",
            "provider_repository_id",
            unique=True,
        ),
        Index("ix_repositories_owner_user_id", "owner_user_id"),
        Index("ix_repositories_full_name", "full_name"),
        Index("ix_repositories_last_indexed_at", "last_indexed_at"),
        Index("ix_repositories_archived_at", "archived_at"),
    )

    owner_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_repository_id: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(511), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    visibility: Mapped[str] = mapped_column(String(30), nullable=False)
    clone_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    web_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_indexed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(nullable=True)

    owner: Mapped["User"] = relationship(back_populates="repositories")
    branches: Mapped[list["RepositoryBranch"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class RepositoryBranch(BaseModel):
    """Branch metadata known for a repository."""

    __tablename__ = "repository_branches"
    __table_args__ = (
        Index(
            "uq_repository_branches_repository_id_name",
            "repository_id",
            "name",
            unique=True,
        ),
        Index(
            "uq_repository_branches_repository_id_default",
            "repository_id",
            unique=True,
            postgresql_where=text("is_default IS TRUE"),
        ),
        Index("ix_repository_branches_head_commit_sha", "head_commit_sha"),
        Index("ix_repository_branches_last_seen_at", "last_seen_at"),
    )

    repository_id: Mapped[UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    head_commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(nullable=True)

    repository: Mapped[Repository] = relationship(back_populates="branches")
