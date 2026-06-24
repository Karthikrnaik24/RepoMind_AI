"""Repository indexing ORM models.

These models map repository_files, code_chunks, embeddings, and indexing_jobs
from docs/DATABASE.md. They intentionally contain no indexing business logic.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel, SoftDeleteBaseModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.chat import Citation
    from app.infrastructure.database.models.repository import Repository, RepositoryBranch
    from app.infrastructure.database.models.user import User


class IndexingJob(BaseModel):
    """Asynchronous repository indexing, embedding, and summary job state."""

    __tablename__ = "indexing_jobs"
    __table_args__ = (
        CheckConstraint(
            "job_type IN ('full_index', 'incremental_index', 'embedding_refresh', "
            "'summary_refresh')",
            name="job_type_valid",
        ),
        CheckConstraint(
            "status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled', 'retrying')",
            name="status_valid",
        ),
        CheckConstraint(
            "progress_total IS NULL OR progress_total >= 0",
            name="progress_total_non_negative",
        ),
        CheckConstraint(
            "progress_completed IS NULL OR progress_completed >= 0",
            name="progress_completed_non_negative",
        ),
        CheckConstraint(
            "progress_total IS NULL OR progress_completed IS NULL "
            "OR progress_completed <= progress_total",
            name="progress_completed_not_greater_than_total",
        ),
        Index(
            "ix_indexing_jobs_repository_id_branch_id_created_at",
            "repository_id",
            "branch_id",
            "created_at",
        ),
        Index("ix_indexing_jobs_status_created_at", "status", "created_at"),
        Index("ix_indexing_jobs_requested_by_user_id", "requested_by_user_id"),
        Index("ix_indexing_jobs_provider_commit_sha", "provider_commit_sha"),
    )

    repository_id: Mapped[UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    branch_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("repository_branches.id", ondelete="SET NULL"),
        nullable=True,
    )
    requested_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="queued")
    provider_commit_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    progress_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    progress_completed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)

    repository: Mapped["Repository"] = relationship(back_populates="indexing_jobs")
    branch: Mapped["RepositoryBranch | None"] = relationship(back_populates="indexing_jobs")
    requested_by: Mapped["User | None"] = relationship(back_populates="requested_indexing_jobs")
    repository_files: Mapped[list["RepositoryFile"]] = relationship(back_populates="indexing_job")
    code_chunks: Mapped[list["CodeChunk"]] = relationship(back_populates="indexing_job")
    embeddings: Mapped[list["Embedding"]] = relationship(back_populates="indexing_job")


class RepositoryFile(SoftDeleteBaseModel):
    """Metadata for a file discovered during repository indexing."""

    __tablename__ = "repository_files"
    __table_args__ = (
        CheckConstraint("size_bytes >= 0", name="size_bytes_non_negative"),
        CheckConstraint("line_count IS NULL OR line_count >= 0", name="line_count_non_negative"),
        Index(
            "uq_repository_files_repository_id_branch_id_path_active",
            "repository_id",
            "branch_id",
            "path",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_repository_files_repository_id_branch_id", "repository_id", "branch_id"),
        Index("ix_repository_files_indexing_job_id", "indexing_job_id"),
        Index("ix_repository_files_language", "language"),
        Index("ix_repository_files_content_hash", "content_hash"),
        Index("ix_repository_files_path", "path"),
    )

    repository_id: Mapped[UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    branch_id: Mapped[UUID] = mapped_column(
        ForeignKey("repository_branches.id", ondelete="CASCADE"),
        nullable=False,
    )
    indexing_job_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("indexing_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    path: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str | None] = mapped_column(String(80), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    blob_sha: Mapped[str | None] = mapped_column(String(80), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    line_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_binary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    indexed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    repository: Mapped["Repository"] = relationship(back_populates="files")
    branch: Mapped["RepositoryBranch"] = relationship(back_populates="files")
    indexing_job: Mapped[IndexingJob | None] = relationship(back_populates="repository_files")
    code_chunks: Mapped[list["CodeChunk"]] = relationship(
        back_populates="repository_file",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    citations: Mapped[list["Citation"]] = relationship(
        back_populates="repository_file",
        passive_deletes=True,
    )


class CodeChunk(BaseModel):
    """Normalized searchable chunk derived from a repository file."""

    __tablename__ = "code_chunks"
    __table_args__ = (
        CheckConstraint("start_line IS NULL OR start_line > 0", name="start_line_positive"),
        CheckConstraint(
            "end_line IS NULL OR start_line IS NULL OR end_line >= start_line",
            name="end_line_not_before_start_line",
        ),
        CheckConstraint("token_count IS NULL OR token_count >= 0", name="token_count_non_negative"),
        Index(
            "uq_code_chunks_repository_file_id_chunk_index",
            "repository_file_id",
            "chunk_index",
            unique=True,
        ),
        Index("ix_code_chunks_indexing_job_id", "indexing_job_id"),
        Index("ix_code_chunks_content_hash", "content_hash"),
        Index("ix_code_chunks_chunk_type", "chunk_type"),
        Index("ix_code_chunks_symbol_name", "symbol_name"),
    )

    repository_file_id: Mapped[UUID] = mapped_column(
        ForeignKey("repository_files.id", ondelete="CASCADE"),
        nullable=False,
    )
    indexing_job_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("indexing_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    symbol_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    repository_file: Mapped[RepositoryFile] = relationship(back_populates="code_chunks")
    indexing_job: Mapped[IndexingJob | None] = relationship(back_populates="code_chunks")
    embeddings: Mapped[list["Embedding"]] = relationship(
        back_populates="code_chunk",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    citations: Mapped[list["Citation"]] = relationship(
        back_populates="code_chunk",
        passive_deletes=True,
    )


class Embedding(BaseModel):
    """pgvector embedding for a code chunk."""

    __tablename__ = "embeddings"
    __table_args__ = (
        CheckConstraint("dimensions > 0", name="dimensions_positive"),
        Index(
            "uq_embeddings_code_chunk_id_model_provider_model_name_content_hash",
            "code_chunk_id",
            "model_provider",
            "model_name",
            "content_hash",
            unique=True,
        ),
        Index("ix_embeddings_model_provider_model_name", "model_provider", "model_name"),
        Index("ix_embeddings_indexing_job_id", "indexing_job_id"),
        Index("ix_embeddings_content_hash", "content_hash"),
        Index(
            "ix_embeddings_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    code_chunk_id: Mapped[UUID] = mapped_column(
        ForeignKey("code_chunks.id", ondelete="CASCADE"),
        nullable=False,
    )
    indexing_job_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("indexing_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    model_provider: Mapped[str] = mapped_column(String(80), nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    code_chunk: Mapped[CodeChunk] = relationship(back_populates="embeddings")
    indexing_job: Mapped[IndexingJob | None] = relationship(back_populates="embeddings")
