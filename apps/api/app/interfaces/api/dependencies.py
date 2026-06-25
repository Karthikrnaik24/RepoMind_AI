"""FastAPI dependency providers.

Providers here compose infrastructure, repositories, and application services
without routes constructing concrete dependencies directly.
"""

import logging
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.services import ChatService, IndexingService, RepositoryService, UserService
from app.config.settings import Settings
from app.config.settings import get_settings as load_settings
from app.core.logging import get_logger as load_logger
from app.infrastructure.auth import SupabaseClient, create_supabase_client
from app.infrastructure.database.session import get_db_session
from app.repositories import (
    ChatRepository,
    IndexingRepository,
    RepositoryRepository,
    UserRepository,
)


def get_settings() -> Settings:
    """Return validated application settings."""

    return load_settings()


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped database session."""

    yield from get_db_session()


def get_logger() -> logging.Logger:
    """Return the application logger for dependency-injected components."""

    return load_logger("repomind.api")


def get_supabase_client() -> SupabaseClient:
    """Return a configured Supabase client placeholder."""

    return create_supabase_client(load_settings())


DbSession = Annotated[Session, Depends(get_db)]


def get_user_repository(db: DbSession) -> UserRepository:
    """Create a user repository for the current request."""

    return UserRepository(db)


def get_repository_repository(db: DbSession) -> RepositoryRepository:
    """Create a repository metadata repository for the current request."""

    return RepositoryRepository(db)


def get_indexing_repository(db: DbSession) -> IndexingRepository:
    """Create an indexing repository for the current request."""

    return IndexingRepository(db)


def get_chat_repository(db: DbSession) -> ChatRepository:
    """Create a chat repository for the current request."""

    return ChatRepository(db)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """Create a user service for the current request."""

    return UserService(user_repository)


def get_repository_service(
    repository_repository: Annotated[
        RepositoryRepository,
        Depends(get_repository_repository),
    ],
) -> RepositoryService:
    """Create a repository service for the current request."""

    return RepositoryService(repository_repository)


def get_indexing_service(
    indexing_repository: Annotated[IndexingRepository, Depends(get_indexing_repository)],
) -> IndexingService:
    """Create an indexing service for the current request."""

    return IndexingService(indexing_repository)


def get_chat_service(
    chat_repository: Annotated[ChatRepository, Depends(get_chat_repository)],
) -> ChatService:
    """Create a chat service for the current request."""

    return ChatService(chat_repository)
