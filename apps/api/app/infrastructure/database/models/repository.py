"""Repository and branch ORM models.

These models map repository metadata from docs/DATABASE.md and the registered
repository management fields used by the platform. They intentionally contain
no repository business logic.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.analysis import ArchitectureSnapshot, DependencyEdge
    from app.infrastructure.database.models.chat import ChatSession, Citation
    from app.infrastructure.database.models.indexing import IndexingJob, RepositoryFile
    from app.infrastructure.database.models.security import AuditLog
    from app.infrastructure.database.models.user import User


class Repository(BaseModel):
    """Connected repository and provider metadata."""

    __tablename__ = "repositories"
    __table_args__ = (
        CheckConstraint(
            "visibility IN ('public', 'private', 'internal')",
            name="visibility_valid",
        ),
        CheckConstraint(
            "sync_status IN ('PENDING', 'READY', 'FAILED')",
            name="sync_status_valid",
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
        Index("ix_repositories_registered_at", "registered_at"),
        Index("ix_repositories_sync_status", "sync_status"),
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
    language: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    clone_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    web_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    sync_status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_indexed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(nullable=True)

    owner: Mapped["User"] = relationship(back_populates="repositories")
    branches: Mapped[list["RepositoryBranch"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    files: Mapped[list["RepositoryFile"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    indexing_jobs: Mapped[list["IndexingJob"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    citations: Mapped[list["Citation"]] = relationship(
        back_populates="repository",
        passive_deletes=True,
    )
    dependency_edges: Mapped[list["DependencyEdge"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    architecture_snapshots: Mapped[list["ArchitectureSnapshot"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="repository",
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
    files: Mapped[list["RepositoryFile"]] = relationship(
        back_populates="branch",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    indexing_jobs: Mapped[list["IndexingJob"]] = relationship(
        back_populates="branch",
        passive_deletes=True,
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="branch",
        passive_deletes=True,
    )
    dependency_edges: Mapped[list["DependencyEdge"]] = relationship(
        back_populates="branch",
        passive_deletes=True,
    )
    architecture_snapshots: Mapped[list["ArchitectureSnapshot"]] = relationship(
        back_populates="branch",
        passive_deletes=True,
    )