"""Create analysis and security tables.

Revision ID: 20260624_0005
Revises: 20260624_0004
Create Date: 2026-06-24

This migration adds dependency graph, architecture snapshot, API key, and audit
log persistence from docs/DATABASE.md. It does not add business logic.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260624_0005"
down_revision: str | None = "20260624_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create dependency_edges, architecture_snapshots, api_keys, and audit_logs."""

    op.create_table(
        "dependency_edges",
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=True),
        sa.Column("source_file_id", sa.Uuid(), nullable=False),
        sa.Column("target_file_id", sa.Uuid(), nullable=True),
        sa.Column("source_symbol", sa.String(length=255), nullable=True),
        sa.Column("target_symbol", sa.String(length=255), nullable=True),
        sa.Column("dependency_type", sa.String(length=80), nullable=False),
        sa.Column("is_external", sa.Boolean(), nullable=False),
        sa.Column("external_package_name", sa.String(length=255), nullable=True),
        sa.Column("confidence", sa.Numeric(8, 6), nullable=True),
        sa.Column("indexing_job_id", sa.Uuid(), nullable=True),
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
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name=op.f("ck_dependency_edges_confidence_between_zero_and_one"),
        ),
        sa.CheckConstraint(
            "dependency_type IN ('import', 'extends', 'calls', 'configures', 'test_covers')",
            name=op.f("ck_dependency_edges_dependency_type_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["repository_branches.id"],
            name=op.f("fk_dependency_edges_branch_id_repository_branches"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["indexing_job_id"],
            ["indexing_jobs.id"],
            name=op.f("fk_dependency_edges_indexing_job_id_indexing_jobs"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            name=op.f("fk_dependency_edges_repository_id_repositories"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_file_id"],
            ["repository_files.id"],
            name=op.f("fk_dependency_edges_source_file_id_repository_files"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_file_id"],
            ["repository_files.id"],
            name=op.f("fk_dependency_edges_target_file_id_repository_files"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dependency_edges")),
    )
    op.create_index(
        "ix_dependency_edges_dependency_type",
        "dependency_edges",
        ["dependency_type"],
    )
    op.create_index(
        "ix_dependency_edges_external_package_name",
        "dependency_edges",
        ["external_package_name"],
    )
    op.create_index(
        "ix_dependency_edges_indexing_job_id",
        "dependency_edges",
        ["indexing_job_id"],
    )
    op.create_index(
        "ix_dependency_edges_repository_id_branch_id",
        "dependency_edges",
        ["repository_id", "branch_id"],
    )
    op.create_index(
        "ix_dependency_edges_source_file_id",
        "dependency_edges",
        ["source_file_id"],
    )
    op.create_index(
        "ix_dependency_edges_target_file_id",
        "dependency_edges",
        ["target_file_id"],
    )

    op.create_table(
        "architecture_snapshots",
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=True),
        sa.Column("indexing_job_id", sa.Uuid(), nullable=True),
        sa.Column("snapshot_type", sa.String(length=80), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("summary_markdown", sa.Text(), nullable=True),
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
            "snapshot_type IN ('repository_overview', 'module_map', 'dependency_map', "
            "'risk_summary')",
            name=op.f("ck_architecture_snapshots_snapshot_type_valid"),
        ),
        sa.CheckConstraint(
            "version > 0",
            name=op.f("ck_architecture_snapshots_version_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["repository_branches.id"],
            name=op.f("fk_architecture_snapshots_branch_id_repository_branches"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["indexing_job_id"],
            ["indexing_jobs.id"],
            name=op.f("fk_architecture_snapshots_indexing_job_id_indexing_jobs"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            name=op.f("fk_architecture_snapshots_repository_id_repositories"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_architecture_snapshots")),
    )
    op.create_index(
        "ix_architecture_snapshots_content_gin",
        "architecture_snapshots",
        ["content"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_architecture_snapshots_indexing_job_id",
        "architecture_snapshots",
        ["indexing_job_id"],
    )
    op.create_index(
        "ix_arch_snapshots_repo_branch_type_created",
        "architecture_snapshots",
        ["repository_id", "branch_id", "snapshot_type", "created_at"],
    )

    op.create_table(
        "api_keys",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("key_prefix", sa.String(length=20), nullable=False),
        sa.Column("key_hash", sa.Text(), nullable=False),
        sa.Column("scopes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
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
            "status IN ('active', 'revoked', 'expired')",
            name=op.f("ck_api_keys_status_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_api_keys_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_api_keys")),
    )
    op.create_index("ix_api_keys_expires_at", "api_keys", ["expires_at"])
    op.create_index("ix_api_keys_key_prefix", "api_keys", ["key_prefix"])
    op.create_index("ix_api_keys_status", "api_keys", ["status"])
    op.create_index("ix_api_keys_user_id_created_at", "api_keys", ["user_id", "created_at"])
    op.create_index("uq_api_keys_key_hash", "api_keys", ["key_hash"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("repository_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("resource_type", sa.String(length=80), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("request_id", sa.String(length=120), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            name=op.f("fk_audit_logs_repository_id_repositories"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_audit_logs_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index("ix_audit_logs_action_created_at", "audit_logs", ["action", "created_at"])
    op.create_index(
        "ix_audit_logs_metadata_gin",
        "audit_logs",
        ["metadata"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_audit_logs_repository_id_created_at",
        "audit_logs",
        ["repository_id", "created_at"],
    )
    op.create_index("ix_audit_logs_request_id", "audit_logs", ["request_id"])
    op.create_index(
        "ix_audit_logs_resource_type_resource_id",
        "audit_logs",
        ["resource_type", "resource_id"],
    )
    op.create_index("ix_audit_logs_user_id_created_at", "audit_logs", ["user_id", "created_at"])


def downgrade() -> None:
    """Drop audit_logs, api_keys, architecture_snapshots, and dependency_edges."""

    op.drop_index("ix_audit_logs_user_id_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_resource_type_resource_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_request_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_repository_id_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_metadata_gin", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action_created_at", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("uq_api_keys_key_hash", table_name="api_keys")
    op.drop_index("ix_api_keys_user_id_created_at", table_name="api_keys")
    op.drop_index("ix_api_keys_status", table_name="api_keys")
    op.drop_index("ix_api_keys_key_prefix", table_name="api_keys")
    op.drop_index("ix_api_keys_expires_at", table_name="api_keys")
    op.drop_table("api_keys")
    op.drop_index(
        "ix_arch_snapshots_repo_branch_type_created",
        table_name="architecture_snapshots",
    )
    op.drop_index(
        "ix_architecture_snapshots_indexing_job_id",
        table_name="architecture_snapshots",
    )
    op.drop_index("ix_architecture_snapshots_content_gin", table_name="architecture_snapshots")
    op.drop_table("architecture_snapshots")
    op.drop_index("ix_dependency_edges_target_file_id", table_name="dependency_edges")
    op.drop_index("ix_dependency_edges_source_file_id", table_name="dependency_edges")
    op.drop_index("ix_dependency_edges_repository_id_branch_id", table_name="dependency_edges")
    op.drop_index("ix_dependency_edges_indexing_job_id", table_name="dependency_edges")
    op.drop_index("ix_dependency_edges_external_package_name", table_name="dependency_edges")
    op.drop_index("ix_dependency_edges_dependency_type", table_name="dependency_edges")
    op.drop_table("dependency_edges")

