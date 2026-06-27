"""Add repository management fields.

Revision ID: 20260627_0008
Revises: 20260626_0007
Create Date: 2026-06-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260627_0008"
down_revision: str | None = "20260626_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add managed repository settings and refresh metadata."""

    op.drop_constraint(op.f("ck_repositories_sync_status_valid"), "repositories", type_="check")
    op.add_column("repositories", sa.Column("display_name", sa.String(length=255), nullable=True))
    op.add_column(
        "repositories",
        sa.Column("favorite", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("repositories", sa.Column("notes", sa.Text(), nullable=True))
    op.add_column(
        "repositories",
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "repositories",
        sa.Column("github_updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_check_constraint(
        op.f("ck_repositories_sync_status_valid"),
        "repositories",
        "sync_status IN ('PENDING', 'READY', 'ERROR')",
    )
    op.create_index("ix_repositories_favorite", "repositories", ["favorite"])
    op.create_index("ix_repositories_last_synced_at", "repositories", ["last_synced_at"])


def downgrade() -> None:
    """Remove managed repository settings and refresh metadata."""

    op.drop_index("ix_repositories_last_synced_at", table_name="repositories")
    op.drop_index("ix_repositories_favorite", table_name="repositories")
    op.drop_constraint(op.f("ck_repositories_sync_status_valid"), "repositories", type_="check")
    op.drop_column("repositories", "github_updated_at")
    op.drop_column("repositories", "last_synced_at")
    op.drop_column("repositories", "notes")
    op.drop_column("repositories", "favorite")
    op.drop_column("repositories", "display_name")
    op.create_check_constraint(
        op.f("ck_repositories_sync_status_valid"),
        "repositories",
        "sync_status IN ('PENDING', 'READY', 'FAILED')",
    )