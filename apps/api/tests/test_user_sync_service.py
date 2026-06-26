from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from app.application.services.user_sync_service import UserSyncService
from app.domain.identity import AuthenticatedUser
from app.infrastructure.database.models import User, UserProfile
from app.repositories.user_repository import UserRepository
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    User.__table__.create(engine)
    UserProfile.__table__.create(engine)
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
        UserProfile.__table__.drop(engine)
        User.__table__.drop(engine)
        engine.dispose()


def authenticated_user(
    *,
    provider_subject: str = "supabase-user-123",
    email: str = "Engineer@Example.com",
    metadata: dict | None = None,
) -> AuthenticatedUser:
    return AuthenticatedUser(
        provider_subject=provider_subject,
        email=email,
        role="member",
        metadata=metadata or {"user_metadata": {"full_name": "Ada Engineer", "avatar_url": "https://example.com/avatar.png"}},
    )


def create_service(session: Session) -> UserSyncService:
    return UserSyncService(UserRepository(session))


def test_new_authenticated_user_creates_user(db_session: Session) -> None:
    result = create_service(db_session).sync_authenticated_user(authenticated_user())

    users = db_session.execute(select(User)).scalars().all()
    assert len(users) == 1
    assert result.user is users[0]
    assert result.user.email == "engineer@example.com"
    assert result.user.auth_provider == "supabase"
    assert result.user.auth_provider_user_id == "supabase-user-123"
    assert result.user.last_login_at is not None


def test_existing_user_updates_last_login_at(db_session: Session) -> None:
    old_login = datetime.now(UTC) - timedelta(days=1)
    user = User(
        email="engineer@example.com",
        auth_provider="supabase",
        auth_provider_user_id="supabase-user-123",
        status="active",
        last_login_at=old_login,
    )
    db_session.add(user)
    db_session.flush()

    result = create_service(db_session).sync_authenticated_user(
        authenticated_user(email="engineer@example.com"),
    )

    assert result.user.id == user.id
    assert result.user.last_login_at is not None
    assert result.user.last_login_at != old_login


def test_email_change_updates_user(db_session: Session) -> None:
    user = User(
        email="old@example.com",
        auth_provider="supabase",
        auth_provider_user_id="supabase-user-123",
        status="active",
    )
    db_session.add(user)
    db_session.flush()

    result = create_service(db_session).sync_authenticated_user(
        authenticated_user(email="new@example.com"),
    )

    assert result.user.id == user.id
    assert result.user.email == "new@example.com"


def test_profile_created(db_session: Session) -> None:
    result = create_service(db_session).sync_authenticated_user(authenticated_user())

    assert result.profile.user_id == result.user.id
    assert result.profile.display_name == "Ada Engineer"
    assert result.profile.avatar_url == "https://example.com/avatar.png"


def test_profile_updated_from_metadata(db_session: Session) -> None:
    user = User(
        email="engineer@example.com",
        auth_provider="supabase",
        auth_provider_user_id="supabase-user-123",
        status="active",
    )
    user.profile = UserProfile(display_name="Old Name", avatar_url="https://example.com/old.png")
    db_session.add(user)
    db_session.flush()

    result = create_service(db_session).sync_authenticated_user(
        authenticated_user(
            email="engineer@example.com",
            metadata={"user_metadata": {"name": "New Name", "avatar_url": "https://example.com/new.png"}},
        ),
    )

    assert result.profile.display_name == "New Name"
    assert result.profile.avatar_url == "https://example.com/new.png"

