"""Create indexing, file, chunk, and embedding tables.

Revision ID: 20260624_0003
Revises: 20260624_0002
Create Date: 2026-06-24

This migration adds repository indexing persistence from docs/DATABASE.md.
It does not add indexing business logic.
"""

import os
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "20260624_0003"
down_revision: str | None = "20260624_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
LOCAL_DEVELOPMENT_ENVIRONMENTS = {"development", "local", "test", "testing"}


def _is_local_development() -> bool:
    """Return whether this migration is running in a local/test environment."""

    return os.getenv("APP_ENV", "development").lower() in LOCAL_DEVELOPMENT_ENVIRONMENTS


def _is_pgvector_available() -> bool:
    """Return whether PostgreSQL can install the pgvector extension."""

    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return False

    return (
        bind.execute(
            sa.text("SELECT 1 FROM pg_available_extensions WHERE name = 'vector'"),
        ).scalar()
        is not None
    )


def _should_use_pgvector() -> bool:
    """Require pgvector in production, but allow a local v0.2.0 fallback."""

    if _is_pgvector_available():
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
        return True

    if _is_local_development():
        # TODO: pgvector is required before v0.3.0 Repository Intelligence.
        # Local v0.2.0 development can migrate without vector because indexing,
        # embeddings, and AI retrieval are intentionally not active yet.
        return False

    msg = "pgvector extension is required outside local development."
    raise RuntimeError(msg)


def _index_exists(table_name: str, index_name: str) -> bool:
    """Return whether an index exists before attempting a conditional drop."""

    inspector = sa.inspect(op.get_bind())
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))

def upgrade() -> None:
    """Create indexing_jobs, repository_files, code_chunks, and embeddings."""

    use_pgvector = _should_use_pgvector()

    op.create_table(
        "indexing_jobs",
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=True),
        sa.Column("requested_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("provider_commit_sha", sa.String(length=40), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=120), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("progress_total", sa.Integer(), nullable=True),
        sa.Column("progress_completed", sa.Integer(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "job_type IN ('full_index', 'incremental_index', 'embedding_refresh', "
            "'summary_refresh')",
            name=op.f("ck_indexing_jobs_job_type_valid"),
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled', 'retrying')",
            name=op.f("ck_indexing_jobs_status_valid"),
        ),
        sa.CheckConstraint(
            "progress_total IS NULL OR progress_total >= 0",
            name=op.f("ck_indexing_jobs_progress_total_non_negative"),
        ),
        sa.CheckConstraint(
            "progress_completed IS NULL OR progress_completed >= 0",
            name=op.f("ck_indexing_jobs_progress_completed_non_negative"),
        ),
        sa.CheckConstraint(
            "progress_total IS NULL OR progress_completed IS NULL "
            "OR progress_completed <= progress_total",
            name=op.f("ck_indexing_jobs_progress_completed_not_greater_than_total"),
        ),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["repository_branches.id"],
            name=op.f("fk_indexing_jobs_branch_id_repository_branches"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            name=op.f("fk_indexing_jobs_repository_id_repositories"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"],
            ["users.id"],
            name=op.f("fk_indexing_jobs_requested_by_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_indexing_jobs")),
    )
    op.create_index(
        "ix_indexing_jobs_provider_commit_sha",
        "indexing_jobs",
        ["provider_commit_sha"],
    )
    op.create_index(
        "ix_indexing_jobs_repository_id_branch_id_created_at",
        "indexing_jobs",
        ["repository_id", "branch_id", "created_at"],
    )
    op.create_index(
        "ix_indexing_jobs_requested_by_user_id",
        "indexing_jobs",
        ["requested_by_user_id"],
    )
    op.create_index(
        "ix_indexing_jobs_status_created_at",
        "indexing_jobs",
        ["status", "created_at"],
    )

    op.create_table(
        "repository_files",
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("indexing_job_id", sa.Uuid(), nullable=True),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=80), nullable=True),
        sa.Column("mime_type", sa.String(length=120), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("blob_sha", sa.String(length=80), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("line_count", sa.Integer(), nullable=True),
        sa.Column("is_binary", sa.Boolean(), nullable=False),
        sa.Column("is_generated", sa.Boolean(), nullable=False),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "line_count IS NULL OR line_count >= 0",
            name=op.f("ck_repository_files_line_count_non_negative"),
        ),
        sa.CheckConstraint(
            "size_bytes >= 0",
            name=op.f("ck_repository_files_size_bytes_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["repository_branches.id"],
            name=op.f("fk_repository_files_branch_id_repository_branches"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["indexing_job_id"],
            ["indexing_jobs.id"],
            name=op.f("fk_repository_files_indexing_job_id_indexing_jobs"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            name=op.f("fk_repository_files_repository_id_repositories"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_repository_files")),
    )
    op.create_index("ix_repository_files_content_hash", "repository_files", ["content_hash"])
    op.create_index("ix_repository_files_indexing_job_id", "repository_files", ["indexing_job_id"])
    op.create_index("ix_repository_files_language", "repository_files", ["language"])
    op.create_index("ix_repository_files_path", "repository_files", ["path"])
    op.create_index(
        "ix_repository_files_repository_id_branch_id",
        "repository_files",
        ["repository_id", "branch_id"],
    )
    op.create_index(
        "uq_repository_files_repository_id_branch_id_path_active",
        "repository_files",
        ["repository_id", "branch_id", "path"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "code_chunks",
        sa.Column("repository_file_id", sa.Uuid(), nullable=False),
        sa.Column("indexing_job_id", sa.Uuid(), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_type", sa.String(length=50), nullable=True),
        sa.Column("symbol_name", sa.String(length=255), nullable=True),
        sa.Column("start_line", sa.Integer(), nullable=True),
        sa.Column("end_line", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "end_line IS NULL OR start_line IS NULL OR end_line >= start_line",
            name=op.f("ck_code_chunks_end_line_not_before_start_line"),
        ),
        sa.CheckConstraint(
            "start_line IS NULL OR start_line > 0",
            name=op.f("ck_code_chunks_start_line_positive"),
        ),
        sa.CheckConstraint(
            "token_count IS NULL OR token_count >= 0",
            name=op.f("ck_code_chunks_token_count_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["indexing_job_id"],
            ["indexing_jobs.id"],
            name=op.f("fk_code_chunks_indexing_job_id_indexing_jobs"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["repository_file_id"],
            ["repository_files.id"],
            name=op.f("fk_code_chunks_repository_file_id_repository_files"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_code_chunks")),
    )
    op.create_index("ix_code_chunks_chunk_type", "code_chunks", ["chunk_type"])
    op.create_index("ix_code_chunks_content_hash", "code_chunks", ["content_hash"])
    op.create_index("ix_code_chunks_indexing_job_id", "code_chunks", ["indexing_job_id"])
    op.create_index("ix_code_chunks_symbol_name", "code_chunks", ["symbol_name"])
    op.create_index(
        "uq_code_chunks_repository_file_id_chunk_index",
        "code_chunks",
        ["repository_file_id", "chunk_index"],
        unique=True,
    )

    op.create_table(
        "embeddings",
        sa.Column("code_chunk_id", sa.Uuid(), nullable=False),
        sa.Column("indexing_job_id", sa.Uuid(), nullable=True),
        sa.Column("model_provider", sa.String(length=80), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("dimensions", sa.Integer(), nullable=False),
        sa.Column(
            "embedding",
            Vector() if use_pgvector else postgresql.JSONB(astext_type=sa.Text()),
            nullable=not use_pgvector,
        ),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("dimensions > 0", name=op.f("ck_embeddings_dimensions_positive")),
        sa.ForeignKeyConstraint(
            ["code_chunk_id"],
            ["code_chunks.id"],
            name=op.f("fk_embeddings_code_chunk_id_code_chunks"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["indexing_job_id"],
            ["indexing_jobs.id"],
            name=op.f("fk_embeddings_indexing_job_id_indexing_jobs"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_embeddings")),
    )
    op.create_index("ix_embeddings_content_hash", "embeddings", ["content_hash"])
    op.create_index("ix_embeddings_indexing_job_id", "embeddings", ["indexing_job_id"])
    op.create_index(
        "ix_embeddings_model_provider_model_name",
        "embeddings",
        ["model_provider", "model_name"],
    )
    op.create_index(
        "uq_embeddings_chunk_model_hash",
        "embeddings",
        ["code_chunk_id", "model_provider", "model_name", "content_hash"],
        unique=True,
    )
    if use_pgvector:
        op.create_index(
            "ix_embeddings_embedding_hnsw",
            "embeddings",
            ["embedding"],
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        )


def downgrade() -> None:
    """Drop embeddings, code_chunks, repository_files, and indexing_jobs."""

    if _index_exists("embeddings", "ix_embeddings_embedding_hnsw"):
        op.drop_index("ix_embeddings_embedding_hnsw", table_name="embeddings")
    op.drop_index(
        "uq_embeddings_chunk_model_hash",
        table_name="embeddings",
    )
    op.drop_index("ix_embeddings_model_provider_model_name", table_name="embeddings")
    op.drop_index("ix_embeddings_indexing_job_id", table_name="embeddings")
    op.drop_index("ix_embeddings_content_hash", table_name="embeddings")
    op.drop_table("embeddings")
    op.drop_index("uq_code_chunks_repository_file_id_chunk_index", table_name="code_chunks")
    op.drop_index("ix_code_chunks_symbol_name", table_name="code_chunks")
    op.drop_index("ix_code_chunks_indexing_job_id", table_name="code_chunks")
    op.drop_index("ix_code_chunks_content_hash", table_name="code_chunks")
    op.drop_index("ix_code_chunks_chunk_type", table_name="code_chunks")
    op.drop_table("code_chunks")
    op.drop_index(
        "uq_repository_files_repository_id_branch_id_path_active",
        table_name="repository_files",
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.drop_index("ix_repository_files_repository_id_branch_id", table_name="repository_files")
    op.drop_index("ix_repository_files_path", table_name="repository_files")
    op.drop_index("ix_repository_files_language", table_name="repository_files")
    op.drop_index("ix_repository_files_indexing_job_id", table_name="repository_files")
    op.drop_index("ix_repository_files_content_hash", table_name="repository_files")
    op.drop_table("repository_files")
    op.drop_index("ix_indexing_jobs_status_created_at", table_name="indexing_jobs")
    op.drop_index("ix_indexing_jobs_requested_by_user_id", table_name="indexing_jobs")
    op.drop_index("ix_indexing_jobs_repository_id_branch_id_created_at", table_name="indexing_jobs")
    op.drop_index("ix_indexing_jobs_provider_commit_sha", table_name="indexing_jobs")
    op.drop_table("indexing_jobs")



