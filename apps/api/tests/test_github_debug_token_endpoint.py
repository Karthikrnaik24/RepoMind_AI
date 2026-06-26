from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest
from app.core.exceptions import AuthenticationException
from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.dependencies import get_identity_provider
from app.main import create_app
from httpx import ASGITransport, AsyncClient

SAMPLE_ACCESS_VALUE = "sample-github-access-value"


class FakeIdentityProvider:
    def __init__(self, user: AuthenticatedUser | None = None) -> None:
        self.user = user

    def verify_token(self, _: str) -> AuthenticatedUser:
        if self.user is None:
            raise AuthenticationException("Invalid JWT.", code="invalid_token")
        return self.user


@asynccontextmanager
async def create_test_client(user: AuthenticatedUser | None = None) -> AsyncIterator[AsyncClient]:
    app = create_app()
    app.dependency_overrides[get_identity_provider] = lambda: FakeIdentityProvider(user)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()


def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer sample-jwt"}


@pytest.mark.asyncio
async def test_debug_token_reports_linked_account() -> None:
    user = AuthenticatedUser(
        provider_subject="subject",
        email="user@example.com",
        metadata={
            "identities": [
                {"provider": "github", "identity_data": {"provider_token": SAMPLE_ACCESS_VALUE}}
            ]
        },
    )

    async with create_test_client(user) as client:
        response = await client.get("/api/v1/github/debug-token", headers=auth_headers())

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "success": True,
        "data": {"github_linked": True, "token_available": True, "provider": "github"},
        "meta": {},
    }
    assert SAMPLE_ACCESS_VALUE not in response.text


@pytest.mark.asyncio
async def test_debug_token_reports_missing_token() -> None:
    user = AuthenticatedUser(
        provider_subject="subject",
        email="user@example.com",
        metadata={"identities": [{"provider": "github", "identity_data": {}}]},
    )

    async with create_test_client(user) as client:
        response = await client.get("/api/v1/github/debug-token", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()["data"] == {
        "github_linked": True,
        "token_available": False,
        "provider": "github",
    }


@pytest.mark.asyncio
async def test_debug_token_reports_provider_not_linked() -> None:
    user = AuthenticatedUser(
        provider_subject="subject",
        email="user@example.com",
        metadata={"identities": [{"provider": "google", "identity_data": {}}]},
    )

    async with create_test_client(user) as client:
        response = await client.get("/api/v1/github/debug-token", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()["data"] == {
        "github_linked": False,
        "token_available": False,
        "provider": "github",
    }


@pytest.mark.asyncio
async def test_debug_token_endpoint_is_protected() -> None:
    user = AuthenticatedUser(provider_subject="subject", email="user@example.com")

    async with create_test_client(user) as client:
        response = await client.get("/api/v1/github/debug-token")

    assert response.status_code == 401
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_debug_token_never_serializes_token() -> None:
    user = AuthenticatedUser(
        provider_subject="subject",
        email="user@example.com",
        metadata={"github_access_token": SAMPLE_ACCESS_VALUE, "providers": ["github"]},
    )

    async with create_test_client(user) as client:
        response = await client.get("/api/v1/github/debug-token", headers=auth_headers())

    assert response.status_code == 200
    assert SAMPLE_ACCESS_VALUE not in response.text