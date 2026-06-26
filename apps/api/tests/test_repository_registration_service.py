from collections.abc import Iterator

import pytest
from app.application.services.repository_registration_service import (
    RepositoryRegistrationInput,
    RepositoryRegistrationService,
)
from app.core.exceptions import AuthorizationException, ConflictException, ResourceNotFoundException
from app.domain.github import RepositorySummary
from app.domain.identity import AuthenticatedUser
from app.infrastructure.database.models import Repository, User
from app.repositories.repository_repository import RepositoryRepository
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from tests.test_github_service import repository_payload


class FakeGitHubService:
    def __init__(self, repository: RepositorySummary) -> None:
        self.repository = repository
        self.last_full_name: str | None = None
        self.last_user: AuthenticatedUser | None = None

    def get_repository_by_full_name(
        self,
        authenticated_user: AuthenticatedUser,
        *,
        full_name: str,
    ) -> RepositorySummary:
        self.last_user = authenticated_user
        self.last_full_name = full_name
        return self.repository


@pytest.fixture
def db_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    User.__table__.create(engine)
    Repository.__table__.create(engine)
    testing_session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    session = testing_session()
    try:
        yield session
    finally:
        session.close()
        Repository.__table__.drop(engine)
        User.__table__.drop(engine)
        engine.dispose()


@pytest.fixture
def owner(db_session: Session) -> User:
    user = User(
        email="engineer@example.com",
        auth_provider="supabase",
        auth_provider_user_id="supabase-user-123",
        status="active",
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def authenticated_user() -> AuthenticatedUser:
    return AuthenticatedUser(provider_subject="supabase-user-123", email="engineer@example.com")


def create_service(summary: RepositorySummary, session: Session) -> RepositoryRegistrationService:
    return RepositoryRegistrationService(
        RepositoryRepository(session),
        FakeGitHubService(summary),  # type: ignore[arg-type]
    )


def registration_input() -> RepositoryRegistrationInput:
    return RepositoryRegistrationInput(
        github_repository_id="123",
        full_name="Karthikrnaik24/RepoMind_AI",
        default_branch="main",
    )


def test_successful_registration_persists_repository(
    db_session: Session,
    owner: User,
    authenticated_user: AuthenticatedUser,
) -> None:
    service = create_service(RepositorySummary.from_github_api(repository_payload()), db_session)

    repository = service.register_repository(
        owner_user_id=owner.id,
        authenticated_user=authenticated_user,
        registration_input=registration_input(),
    )

    persisted_repository = db_session.execute(select(Repository)).scalar_one()
    assert repository is persisted_repository
    assert persisted_repository.owner_user_id == owner.id
    assert persisted_repository.provider == "github"
    assert persisted_repository.provider_repository_id == "123"
    assert persisted_repository.full_name == "Karthikrnaik24/RepoMind_AI"
    assert persisted_repository.owner_name == "Karthikrnaik24"
    assert persisted_repository.language == "TypeScript"
    assert persisted_repository.description == "AI software engineer for GitHub repositories"
    assert persisted_repository.web_url == "https://github.com/Karthikrnaik24/RepoMind_AI"
    assert persisted_repository.sync_status == "PENDING"
    assert persisted_repository.registered_at is not None


def test_duplicate_registration_is_rejected(
    db_session: Session,
    owner: User,
    authenticated_user: AuthenticatedUser,
) -> None:
    service = create_service(RepositorySummary.from_github_api(repository_payload()), db_session)
    service.register_repository(
        owner_user_id=owner.id,
        authenticated_user=authenticated_user,
        registration_input=registration_input(),
    )

    with pytest.raises(ConflictException) as exc_info:
        service.register_repository(
            owner_user_id=owner.id,
            authenticated_user=authenticated_user,
            registration_input=registration_input(),
        )

    assert exc_info.value.code == "repository_registered"


def test_repository_id_validation_prevents_unavailable_repository(
    db_session: Session,
    owner: User,
    authenticated_user: AuthenticatedUser,
) -> None:
    service = create_service(RepositorySummary.from_github_api(repository_payload()), db_session)
    invalid_input = RepositoryRegistrationInput(
        github_repository_id="999",
        full_name="Karthikrnaik24/RepoMind_AI",
        default_branch="main",
    )

    with pytest.raises(ResourceNotFoundException) as exc_info:
        service.register_repository(
            owner_user_id=owner.id,
            authenticated_user=authenticated_user,
            registration_input=invalid_input,
        )

    assert exc_info.value.code == "github_repository_not_found"


def test_default_branch_validation_rejects_mismatched_repository(
    db_session: Session,
    owner: User,
    authenticated_user: AuthenticatedUser,
) -> None:
    service = create_service(RepositorySummary.from_github_api(repository_payload()), db_session)
    invalid_input = RepositoryRegistrationInput(
        github_repository_id="123",
        full_name="Karthikrnaik24/RepoMind_AI",
        default_branch="develop",
    )

    with pytest.raises(AuthorizationException) as exc_info:
        service.register_repository(
            owner_user_id=owner.id,
            authenticated_user=authenticated_user,
            registration_input=invalid_input,
        )

    assert exc_info.value.code == "repository_validation_failed"


def test_list_registered_repositories_returns_only_user_owned_repositories(
    db_session: Session,
    owner: User,
    authenticated_user: AuthenticatedUser,
) -> None:
    other_owner = User(
        email="other@example.com",
        auth_provider="supabase",
        auth_provider_user_id="other-user-123",
        status="active",
    )
    db_session.add(other_owner)
    db_session.flush()
    service = create_service(RepositorySummary.from_github_api(repository_payload()), db_session)
    repository = service.register_repository(
        owner_user_id=owner.id,
        authenticated_user=authenticated_user,
        registration_input=registration_input(),
    )
    RepositoryRepository(db_session).create_registered_repository(
        owner_user_id=other_owner.id,
        provider_repository_id="456",
        owner_name="Other",
        name="other-repo",
        full_name="Other/other-repo",
        default_branch="main",
        visibility="public",
        language=None,
        description=None,
        web_url="https://github.com/Other/other-repo",
    )
    db_session.flush()

    repositories = service.list_registered_repositories(owner.id)

    assert repositories == [repository]

def test_get_registered_repository_returns_owner_scoped_repository(
    db_session: Session,
    owner: User,
    authenticated_user: AuthenticatedUser,
) -> None:
    service = create_service(RepositorySummary.from_github_api(repository_payload()), db_session)
    repository = service.register_repository(
        owner_user_id=owner.id,
        authenticated_user=authenticated_user,
        registration_input=registration_input(),
    )

    result = service.get_registered_repository(
        owner_user_id=owner.id,
        repository_id=repository.id,
    )

    assert result is repository


def test_get_registered_repository_hides_unowned_repository(
    db_session: Session,
    owner: User,
    authenticated_user: AuthenticatedUser,
) -> None:
    other_owner = User(
        email="other-detail@example.com",
        auth_provider="supabase",
        auth_provider_user_id="other-detail-user-123",
        status="active",
    )
    db_session.add(other_owner)
    db_session.flush()
    service = create_service(RepositorySummary.from_github_api(repository_payload()), db_session)
    repository = service.register_repository(
        owner_user_id=owner.id,
        authenticated_user=authenticated_user,
        registration_input=registration_input(),
    )

    with pytest.raises(ResourceNotFoundException) as exc_info:
        service.get_registered_repository(
            owner_user_id=other_owner.id,
            repository_id=repository.id,
        )

    assert exc_info.value.code == "repository_not_found"
