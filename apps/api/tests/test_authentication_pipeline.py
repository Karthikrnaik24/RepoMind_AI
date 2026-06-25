from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.core.exceptions import AuthenticationException
from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.dependencies import get_identity_provider
from app.main import create_app
from httpx import ASGITransport, AsyncClient


class FakeIdentityProvider:
    """Mock identity provider used by authentication pipeline tests."""

    def __init__(
        self,
        *,
        user: AuthenticatedUser | None = None,
        exception: AuthenticationException | None = None,
    ) -> None:
        self.user = user
        self.exception = exception
        self.last_token: str | None = None

    def verify_token(self, token: str) -> AuthenticatedUser:
        self.last_token = token
        if self.exception is not None:
            raise self.exception
        if self.user is None:
            raise AuthenticationException("Invalid JWT.", code="invalid_token")
        return self.user


@asynccontextmanager
async def create_test_client(
    provider: FakeIdentityProvider | None = None,
) -> AsyncIterator[AsyncClient]:
    app = create_app()
    if provider is not None:
        app.dependency_overrides[get_identity_provider] = lambda: provider
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


async def test_me_returns_401_when_authorization_header_is_missing() -> None:
    async with create_test_client() as client:
        response = await client.get("/api/v1/me")

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {
            "code": "missing_token",
            "message": "Missing Authorization bearer token.",
        },
    }


async def test_me_returns_401_for_invalid_bearer_format() -> None:
    async with create_test_client() as client:
        response = await client.get("/api/v1/me", headers={"Authorization": "Token abc"})

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {
            "code": "invalid_authorization_header",
            "message": "Authorization header must use the Bearer scheme.",
        },
    }


async def test_me_returns_401_for_invalid_jwt() -> None:
    sample = "sample-invalid-value"
    provider = FakeIdentityProvider(
        exception=AuthenticationException("Invalid JWT.", code="invalid_token"),
    )

    async with create_test_client(provider) as client:
        response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {sample}"})

    assert provider.last_token == sample
    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {
            "code": "invalid_token",
            "message": "Invalid JWT.",
        },
    }


async def test_me_returns_401_for_expired_jwt() -> None:
    sample = "sample-expired-value"
    provider = FakeIdentityProvider(
        exception=AuthenticationException("JWT has expired.", code="token_expired"),
    )

    async with create_test_client(provider) as client:
        response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {sample}"})

    assert provider.last_token == sample
    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {
            "code": "token_expired",
            "message": "JWT has expired.",
        },
    }


async def test_me_returns_authenticated_user_for_valid_jwt() -> None:
    sample = "sample-valid-value"
    provider = FakeIdentityProvider(
        user=AuthenticatedUser(
            provider_subject="supabase-user-123",
            email="user@example.com",
            role="member",
            metadata={"team": "platform"},
        ),
    )

    async with create_test_client(provider) as client:
        response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {sample}"})

    assert provider.last_token == sample
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "id": "supabase-user-123",
            "email": "user@example.com",
            "provider": "supabase",
            "role": "member",
            "metadata": {"team": "platform"},
        },
        "meta": {},
    }
