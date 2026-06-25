from unittest.mock import Mock

from app.application.services import ChatService, IndexingService, RepositoryService, UserService
from app.infrastructure.database.models import User
from app.interfaces.api import dependencies
from app.repositories import (
    ChatRepository,
    IndexingRepository,
    RepositoryRepository,
    UserRepository,
)
from sqlalchemy.orm import Session


def test_repository_layer_can_stage_entities() -> None:
    session = Mock(spec=Session)
    repository = UserRepository(session)
    user = User(
        email="layer@example.com",
        auth_provider="github",
        auth_provider_user_id="layer-1",
        status="active",
    )

    result = repository.add(user)

    assert result is user
    session.add.assert_called_once_with(user)


def test_repository_providers_create_repository_instances() -> None:
    session = Mock(spec=Session)

    assert isinstance(dependencies.get_user_repository(session), UserRepository)
    assert isinstance(dependencies.get_repository_repository(session), RepositoryRepository)
    assert isinstance(dependencies.get_indexing_repository(session), IndexingRepository)
    assert isinstance(dependencies.get_chat_repository(session), ChatRepository)


def test_service_providers_inject_repository_dependencies() -> None:
    session = Mock(spec=Session)
    user_repository = UserRepository(session)
    repository_repository = RepositoryRepository(session)
    indexing_repository = IndexingRepository(session)
    chat_repository = ChatRepository(session)

    user_service = dependencies.get_user_service(user_repository)
    repository_service = dependencies.get_repository_service(repository_repository)
    indexing_service = dependencies.get_indexing_service(indexing_repository)
    chat_service = dependencies.get_chat_service(chat_repository)

    assert isinstance(user_service, UserService)
    assert user_service.user_repository is user_repository
    assert isinstance(repository_service, RepositoryService)
    assert repository_service.repository_repository is repository_repository
    assert isinstance(indexing_service, IndexingService)
    assert indexing_service.indexing_repository is indexing_repository
    assert isinstance(chat_service, ChatService)
    assert chat_service.chat_repository is chat_repository


def test_logger_provider_returns_named_logger() -> None:
    logger = dependencies.get_logger()

    assert logger.name == "repomind.api"
