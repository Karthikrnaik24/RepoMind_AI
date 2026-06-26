"""Add user roles for RBAC foundation.

Revision ID: 20260624_0006
Revises: 20260624_0005
Create Date: 2026-06-26

This migration adds the local user role used by the authorization layer. It does
not add RBAC enforcement beyond storing the role value.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260624_0006"
down_revision: str | None = "20260624_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add role storage to users."""

    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=30),
            server_default="user",
            nullable=False,
        ),
    )
    op.create_check_constraint(
        op.f("ck_users_role_valid"),
        "users",
        "role IN ('user', 'admin')",
    )
    op.create_index("ix_users_role", "users", ["role"], unique=False)


def downgrade() -> None:
    """Remove role storage from users."""

    op.drop_index("ix_users_role", table_name="users")
    op.drop_constraint(op.f("ck_users_role_valid"), "users", type_="check")
    op.drop_column("users", "role")
