"""Repository analysis ORM models.

These models map dependency_edges and architecture_snapshots from
docs/DATABASE.md. They store derived repository intelligence only and do not
contain parsing, graph-building, or summarization business logic.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.indexing import IndexingJob, RepositoryFile
    from app.infrastructure.database.models.repository import Repository, RepositoryBranch


class DependencyEdge(BaseModel):
    """Discovered dependency relationship between files, symbols, or packages."""

    __tablename__ = "dependency_edges"
    __table_args__ = (
        CheckConstraint(
            "dependency_type IN ('import', 'extends', 'calls', 'configures', 'test_covers')",
            name="dependency_type_valid",
        ),
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="confidence_between_zero_and_one",
        ),
        Index("ix_dependency_edges_repository_id_branch_id", "repository_id", "branch_id"),
        Index("ix_dependency_edges_source_file_id", "source_file_id"),
        Index("ix_dependency_edges_target_file_id", "target_file_id"),
        Index("ix_dependency_edges_dependency_type", "dependency_type"),
        Index("ix_dependency_edges_external_package_name", "external_package_name"),
        Index("ix_dependency_edges_indexing_job_id", "indexing_job_id"),
    )

    repository_id: Mapped[UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    branch_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("repository_branches.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_file_id: Mapped[UUID] = mapped_column(
        ForeignKey("repository_files.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_file_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("repository_files.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_symbol: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_symbol: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dependency_type: Mapped[str] = mapped_column(String(80), nullable=False)
    is_external: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    external_package_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(8, 6), nullable=True)
    indexing_job_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("indexing_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )

    repository: Mapped["Repository"] = relationship(back_populates="dependency_edges")
    branch: Mapped["RepositoryBranch | None"] = relationship(back_populates="dependency_edges")
    source_file: Mapped["RepositoryFile"] = relationship(
        back_populates="source_dependency_edges",
        foreign_keys=[source_file_id],
    )
    target_file: Mapped["RepositoryFile | None"] = relationship(
        back_populates="target_dependency_edges",
        foreign_keys=[target_file_id],
    )
    indexing_job: Mapped["IndexingJob | None"] = relationship(back_populates="dependency_edges")


class ArchitectureSnapshot(BaseModel):
    """Generated architecture summary or structured repository snapshot."""

    __tablename__ = "architecture_snapshots"
    __table_args__ = (
        CheckConstraint(
            "snapshot_type IN ('repository_overview', 'module_map', 'dependency_map', "
            "'risk_summary')",
            name="snapshot_type_valid",
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_architecture_snapshots_repository_id_branch_id_snapshot_type_created_at",
            "repository_id",
            "branch_id",
            "snapshot_type",
            "created_at",
        ),
        Index("ix_architecture_snapshots_indexing_job_id", "indexing_job_id"),
        Index("ix_architecture_snapshots_content_gin", "content", postgresql_using="gin"),
    )

    repository_id: Mapped[UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    branch_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("repository_branches.id", ondelete="SET NULL"),
        nullable=True,
    )
    indexing_job_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("indexing_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    snapshot_type: Mapped[str] = mapped_column(String(80), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    summary_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)

    repository: Mapped["Repository"] = relationship(back_populates="architecture_snapshots")
    branch: Mapped["RepositoryBranch | None"] = relationship(
        back_populates="architecture_snapshots",
    )
    indexing_job: Mapped["IndexingJob | None"] = relationship(
        back_populates="architecture_snapshots",
    )
