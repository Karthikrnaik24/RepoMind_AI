"""Create chat session, message, and citation tables.

Revision ID: 20260624_0004
Revises: 20260624_0003
Create Date: 2026-06-24

This migration adds chat persistence from docs/DATABASE.md. It does not add
chat application behavior.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260624_0004"
down_revision: str | None = "20260624_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create chat_sessions, chat_messages, and citations."""

    op.create_table(
        "chat_sessions",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
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
            "status IN ('active', 'archived')",
            name=op.f("ck_chat_sessions_status_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["repository_branches.id"],
            name=op.f("fk_chat_sessions_branch_id_repository_branches"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            name=op.f("fk_chat_sessions_repository_id_repositories"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_chat_sessions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chat_sessions")),
    )
    op.create_index("ix_chat_sessions_branch_id", "chat_sessions", ["branch_id"])
    op.create_index(
        "ix_chat_sessions_repository_id_updated_at",
        "chat_sessions",
        ["repository_id", "updated_at"],
    )
    op.create_index("ix_chat_sessions_status", "chat_sessions", ["status"])
    op.create_index(
        "ix_chat_sessions_user_id_updated_at",
        "chat_sessions",
        ["user_id", "updated_at"],
    )

    op.create_table(
        "chat_messages",
        sa.Column("chat_session_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model_provider", sa.String(length=80), nullable=True),
        sa.Column("model_name", sa.String(length=120), nullable=True),
        sa.Column("prompt_version", sa.String(length=80), nullable=True),
        sa.Column("token_input_count", sa.Integer(), nullable=True),
        sa.Column("token_output_count", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
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
            "role IN ('user', 'assistant', 'system', 'tool')",
            name=op.f("ck_chat_messages_role_valid"),
        ),
        sa.CheckConstraint(
            "latency_ms IS NULL OR latency_ms >= 0",
            name=op.f("ck_chat_messages_latency_ms_non_negative"),
        ),
        sa.CheckConstraint(
            "token_input_count IS NULL OR token_input_count >= 0",
            name=op.f("ck_chat_messages_token_input_count_non_negative"),
        ),
        sa.CheckConstraint(
            "token_output_count IS NULL OR token_output_count >= 0",
            name=op.f("ck_chat_messages_token_output_count_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["chat_session_id"],
            ["chat_sessions.id"],
            name=op.f("fk_chat_messages_chat_session_id_chat_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chat_messages")),
    )
    op.create_index(
        "ix_chat_messages_chat_session_id_created_at",
        "chat_messages",
        ["chat_session_id", "created_at"],
    )
    op.create_index(
        "ix_chat_messages_metadata_gin",
        "chat_messages",
        ["metadata"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_chat_messages_model_provider_model_name",
        "chat_messages",
        ["model_provider", "model_name"],
    )
    op.create_index("ix_chat_messages_role", "chat_messages", ["role"])

    op.create_table(
        "citations",
        sa.Column("chat_message_id", sa.Uuid(), nullable=False),
        sa.Column("code_chunk_id", sa.Uuid(), nullable=False),
        sa.Column("repository_file_id", sa.Uuid(), nullable=False),
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("relevance_score", sa.Numeric(8, 6), nullable=True),
        sa.Column("citation_order", sa.Integer(), nullable=False),
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
            "citation_order >= 0",
            name=op.f("ck_citations_citation_order_non_negative"),
        ),
        sa.CheckConstraint(
            "end_line >= start_line",
            name=op.f("ck_citations_end_line_not_before_start_line"),
        ),
        sa.CheckConstraint(
            "relevance_score IS NULL OR (relevance_score >= 0 AND relevance_score <= 1)",
            name=op.f("ck_citations_relevance_score_between_zero_and_one"),
        ),
        sa.CheckConstraint("start_line > 0", name=op.f("ck_citations_start_line_positive")),
        sa.ForeignKeyConstraint(
            ["chat_message_id"],
            ["chat_messages.id"],
            name=op.f("fk_citations_chat_message_id_chat_messages"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["code_chunk_id"],
            ["code_chunks.id"],
            name=op.f("fk_citations_code_chunk_id_code_chunks"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["repository_file_id"],
            ["repository_files.id"],
            name=op.f("fk_citations_repository_file_id_repository_files"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            name=op.f("fk_citations_repository_id_repositories"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_citations")),
    )
    op.create_index(
        "ix_citations_chat_message_id_citation_order",
        "citations",
        ["chat_message_id", "citation_order"],
    )
    op.create_index("ix_citations_code_chunk_id", "citations", ["code_chunk_id"])
    op.create_index("ix_citations_repository_file_id", "citations", ["repository_file_id"])
    op.create_index("ix_citations_repository_id", "citations", ["repository_id"])


def downgrade() -> None:
    """Drop citations, chat_messages, and chat_sessions."""

    op.drop_index("ix_citations_repository_id", table_name="citations")
    op.drop_index("ix_citations_repository_file_id", table_name="citations")
    op.drop_index("ix_citations_code_chunk_id", table_name="citations")
    op.drop_index("ix_citations_chat_message_id_citation_order", table_name="citations")
    op.drop_table("citations")
    op.drop_index("ix_chat_messages_role", table_name="chat_messages")
    op.drop_index("ix_chat_messages_model_provider_model_name", table_name="chat_messages")
    op.drop_index("ix_chat_messages_metadata_gin", table_name="chat_messages")
    op.drop_index("ix_chat_messages_chat_session_id_created_at", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("ix_chat_sessions_user_id_updated_at", table_name="chat_sessions")
    op.drop_index("ix_chat_sessions_status", table_name="chat_sessions")
    op.drop_index("ix_chat_sessions_repository_id_updated_at", table_name="chat_sessions")
    op.drop_index("ix_chat_sessions_branch_id", table_name="chat_sessions")
    op.drop_table("chat_sessions")
