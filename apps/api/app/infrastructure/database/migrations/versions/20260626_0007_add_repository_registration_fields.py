"""Add repository registration management fields.

Revision ID: 20260626_0007
Revises: 20260624_0006
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260626_0007"
down_revision: str | None = "20260624_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add managed repository registration fields."""

    op.add_column("repositories", sa.Column("language", sa.String(length=120), nullable=True))
    op.add_column("repositories", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "repositories",
        sa.Column("sync_status", sa.String(length=30), nullable=False, server_default="PENDING"),
    )
    op.add_column(
        "repositories",
        sa.Column(
            "registered_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_check_constraint(
        op.f("ck_repositories_sync_status_valid"),
        "repositories",
        "sync_status IN ('PENDING', 'READY', 'FAILED')",
    )
    op.create_index("ix_repositories_registered_at", "repositories", ["registered_at"])
    op.create_index("ix_repositories_sync_status", "repositories", ["sync_status"])


def downgrade() -> None:
    """Remove managed repository registration fields."""

    op.drop_index("ix_repositories_sync_status", table_name="repositories")
    op.drop_index("ix_repositories_registered_at", table_name="repositories")
    op.drop_constraint(op.f("ck_repositories_sync_status_valid"), "repositories", type_="check")
    op.drop_column("repositories", "registered_at")
    op.drop_column("repositories", "sync_status")
    op.drop_column("repositories", "description")
    op.drop_column("repositories", "language")