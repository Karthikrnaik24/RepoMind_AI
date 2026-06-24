"""Create users and user_profiles tables.

Revision ID: 20260624_0001
Revises:
Create Date: 2026-06-24

This migration adds only the user identity and profile tables from
docs/DATABASE.md. It does not add authentication logic.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260624_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create users and user_profiles."""

    op.create_table(
        "users",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("auth_provider", sa.String(length=50), nullable=False),
        sa.Column("auth_provider_user_id", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('active', 'suspended', 'deleted')",
            name=op.f("ck_users_status_valid"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index("ix_users_created_at", "users", ["created_at"], unique=False)
    op.create_index("ix_users_deleted_at", "users", ["deleted_at"], unique=False)
    op.create_index("ix_users_status", "users", ["status"], unique=False)
    op.create_index(
        "uq_users_auth_provider_auth_provider_user_id",
        "users",
        ["auth_provider", "auth_provider_user_id"],
        unique=True,
    )
    op.create_index(
        "uq_users_email_active",
        "users",
        ["email"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("timezone", sa.String(length=80), nullable=True),
        sa.Column("locale", sa.String(length=20), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_profiles_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_profiles")),
        sa.UniqueConstraint("user_id", name=op.f("uq_user_profiles_user_id")),
    )
    op.create_index(
        "ix_user_profiles_display_name",
        "user_profiles",
        ["display_name"],
        unique=False,
    )


def downgrade() -> None:
    """Drop user_profiles and users."""

    op.drop_index("ix_user_profiles_display_name", table_name="user_profiles")
    op.drop_table("user_profiles")
    op.drop_index("uq_users_email_active", table_name="users", postgresql_where=sa.text("deleted_at IS NULL"))
    op.drop_index("uq_users_auth_provider_auth_provider_user_id", table_name="users")
    op.drop_index("ix_users_status", table_name="users")
    op.drop_index("ix_users_deleted_at", table_name="users")
    op.drop_index("ix_users_created_at", table_name="users")
    op.drop_table("users")
