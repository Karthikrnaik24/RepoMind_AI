"""Create repositories and repository_branches tables.

Revision ID: 20260624_0002
Revises: 20260624_0001
Create Date: 2026-06-24

This migration adds repository metadata and branch metadata from
docs/DATABASE.md. It does not add repository business logic.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260624_0002"
down_revision: str | None = "20260624_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create repositories and repository_branches."""

    op.create_table(
        "repositories",
        sa.Column("owner_user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_repository_id", sa.String(length=255), nullable=False),
        sa.Column("owner_name", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=511), nullable=False),
        sa.Column("default_branch", sa.String(length=255), nullable=False),
        sa.Column("visibility", sa.String(length=30), nullable=False),
        sa.Column("clone_url", sa.Text(), nullable=True),
        sa.Column("web_url", sa.Text(), nullable=True),
        sa.Column("last_indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
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
            "visibility IN ('public', 'private', 'internal')",
            name=op.f("ck_repositories_visibility_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_repositories_owner_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_repositories")),
    )
    op.create_index("ix_repositories_archived_at", "repositories", ["archived_at"])
    op.create_index("ix_repositories_full_name", "repositories", ["full_name"])
    op.create_index("ix_repositories_last_indexed_at", "repositories", ["last_indexed_at"])
    op.create_index("ix_repositories_owner_user_id", "repositories", ["owner_user_id"])
    op.create_index(
        "uq_repositories_provider_provider_repository_id",
        "repositories",
        ["provider", "provider_repository_id"],
        unique=True,
    )

    op.create_table(
        "repository_branches",
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("head_commit_sha", sa.String(length=40), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
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
            name=op.f("fk_repository_branches_repository_id_repositories"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_repository_branches")),
    )
    op.create_index(
        "ix_repository_branches_head_commit_sha",
        "repository_branches",
        ["head_commit_sha"],
    )
    op.create_index(
        "ix_repository_branches_last_seen_at",
        "repository_branches",
        ["last_seen_at"],
    )
    op.create_index(
        "uq_repository_branches_repository_id_default",
        "repository_branches",
        ["repository_id"],
        unique=True,
        postgresql_where=sa.text("is_default IS TRUE"),
    )
    op.create_index(
        "uq_repository_branches_repository_id_name",
        "repository_branches",
        ["repository_id", "name"],
        unique=True,
    )


def downgrade() -> None:
    """Drop repository_branches and repositories."""

    op.drop_index("uq_repository_branches_repository_id_name", table_name="repository_branches")
    op.drop_index(
        "uq_repository_branches_repository_id_default",
        table_name="repository_branches",
        postgresql_where=sa.text("is_default IS TRUE"),
    )
    op.drop_index("ix_repository_branches_last_seen_at", table_name="repository_branches")
    op.drop_index("ix_repository_branches_head_commit_sha", table_name="repository_branches")
    op.drop_table("repository_branches")
    op.drop_index("uq_repositories_provider_provider_repository_id", table_name="repositories")
    op.drop_index("ix_repositories_owner_user_id", table_name="repositories")
    op.drop_index("ix_repositories_last_indexed_at", table_name="repositories")
    op.drop_index("ix_repositories_full_name", table_name="repositories")
    op.drop_index("ix_repositories_archived_at", table_name="repositories")
    op.drop_table("repositories")
