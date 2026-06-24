"""Chat session, message, and citation ORM models.

These models map chat_sessions, chat_messages, and citations from
docs/DATABASE.md. They intentionally contain no chat business logic.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.indexing import CodeChunk, RepositoryFile
    from app.infrastructure.database.models.repository import Repository, RepositoryBranch
    from app.infrastructure.database.models.user import User


class ChatSession(BaseModel):
    """User-visible repository chat conversation."""

    __tablename__ = "chat_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'archived')",
            name="status_valid",
        ),
        Index("ix_chat_sessions_user_id_updated_at", "user_id", "updated_at"),
        Index("ix_chat_sessions_repository_id_updated_at", "repository_id", "updated_at"),
        Index("ix_chat_sessions_branch_id", "branch_id"),
        Index("ix_chat_sessions_status", "status"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    repository_id: Mapped[UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    branch_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("repository_branches.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    archived_at: Mapped[datetime | None] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship(back_populates="chat_sessions")
    repository: Mapped["Repository"] = relationship(back_populates="chat_sessions")
    branch: Mapped["RepositoryBranch | None"] = relationship(back_populates="chat_sessions")
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="chat_session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ChatMessage(BaseModel):
    """Immutable message stored within a chat session."""

    __tablename__ = "chat_messages"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system', 'tool')",
            name="role_valid",
        ),
        CheckConstraint(
            "token_input_count IS NULL OR token_input_count >= 0",
            name="token_input_count_non_negative",
        ),
        CheckConstraint(
            "token_output_count IS NULL OR token_output_count >= 0",
            name="token_output_count_non_negative",
        ),
        CheckConstraint("latency_ms IS NULL OR latency_ms >= 0", name="latency_ms_non_negative"),
        Index("ix_chat_messages_chat_session_id_created_at", "chat_session_id", "created_at"),
        Index("ix_chat_messages_role", "role"),
        Index("ix_chat_messages_model_provider_model_name", "model_provider", "model_name"),
        Index("ix_chat_messages_metadata_gin", "metadata", postgresql_using="gin"),
    )

    chat_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model_provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    token_input_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_output_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)

    chat_session: Mapped[ChatSession] = relationship(back_populates="messages")
    citations: Mapped[list["Citation"]] = relationship(
        back_populates="chat_message",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Citation(BaseModel):
    """Source citation linking an assistant message to indexed repository context."""

    __tablename__ = "citations"
    __table_args__ = (
        CheckConstraint("start_line > 0", name="start_line_positive"),
        CheckConstraint("end_line >= start_line", name="end_line_not_before_start_line"),
        CheckConstraint("citation_order >= 0", name="citation_order_non_negative"),
        CheckConstraint(
            "relevance_score IS NULL OR (relevance_score >= 0 AND relevance_score <= 1)",
            name="relevance_score_between_zero_and_one",
        ),
        Index("ix_citations_chat_message_id_citation_order", "chat_message_id", "citation_order"),
        Index("ix_citations_code_chunk_id", "code_chunk_id"),
        Index("ix_citations_repository_file_id", "repository_file_id"),
        Index("ix_citations_repository_id", "repository_id"),
    )

    chat_message_id: Mapped[UUID] = mapped_column(
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        nullable=False,
    )
    code_chunk_id: Mapped[UUID] = mapped_column(
        ForeignKey("code_chunks.id", ondelete="CASCADE"),
        nullable=False,
    )
    repository_file_id: Mapped[UUID] = mapped_column(
        ForeignKey("repository_files.id", ondelete="CASCADE"),
        nullable=False,
    )
    repository_id: Mapped[UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    relevance_score: Mapped[Decimal | None] = mapped_column(Numeric(8, 6), nullable=True)
    citation_order: Mapped[int] = mapped_column(Integer, nullable=False)

    chat_message: Mapped[ChatMessage] = relationship(back_populates="citations")
    code_chunk: Mapped["CodeChunk"] = relationship(back_populates="citations")
    repository_file: Mapped["RepositoryFile"] = relationship(back_populates="citations")
    repository: Mapped["Repository"] = relationship(back_populates="citations")
