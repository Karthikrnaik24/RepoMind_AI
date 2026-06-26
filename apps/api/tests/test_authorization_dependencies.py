from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager

from app.domain.authorization import Role
from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.dependencies import get_identity_provider
from app.infrastructure.database.models import User, UserProfile
from app.interfaces.api.dependencies import get_db
from app.main import create_app
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


class FakeIdentityProvider:
    """Mock identity provider for authorization endpoint tests."""

    def __init__(self, user: AuthenticatedUser) -> None:
        self.user = user

    def verify_token(self, _: str) -> AuthenticatedUser:
        return self.user


@asynccontextmanager
async def create_admin_test_client(
    *,
    local_role: Role | None = None,
    provider: FakeIdentityProvider | None = None,
) -> AsyncIterator[AsyncClient]:
    app = create_app()
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

    if local_role is not None:
        with testing_session() as session:
            user = User(
                email="admin@example.com",
                auth_provider="supabase",
                auth_provider_user_id="supabase-user-123",
                status="active",
                role=local_role.value,
            )
            user.profile = UserProfile(display_name="Admin User")
            session.add(user)
            session.commit()

    def override_get_db() -> Iterator[Session]:
        session = testing_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    if provider is not None:
        app.dependency_overrides[get_identity_provider] = lambda: provider

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        UserProfile.__table__.drop(engine)
        User.__table__.drop(engine)
        engine.dispose()


def authenticated_provider() -> FakeIdentityProvider:
    return FakeIdentityProvider(
        AuthenticatedUser(
            provider_subject="supabase-user-123",
            email="admin@example.com",
            role=None,
            metadata={"user_metadata": {"name": "Admin User"}},
        ),
    )


async def test_user_cannot_access_admin_ping() -> None:
    async with create_admin_test_client(
        local_role=Role.USER,
        provider=authenticated_provider(),
    ) as client:
        response = await client.get(
            "/api/v1/admin/ping",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code == 403
    assert response.json() == {
        "success": False,
        "error": {
            "code": "forbidden",
            "message": "You do not have permission.",
        },
    }


async def test_admin_can_access_admin_ping() -> None:
    async with create_admin_test_client(
        local_role=Role.ADMIN,
        provider=authenticated_provider(),
    ) as client:
        response = await client.get(
            "/api/v1/admin/ping",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {"status": "ok"},
        "meta": {},
    }


async def test_admin_ping_missing_auth_returns_401() -> None:
    async with create_admin_test_client() as client:
        response = await client.get("/api/v1/admin/ping")

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {
            "code": "missing_token",
            "message": "Missing Authorization bearer token.",
        },
    }
