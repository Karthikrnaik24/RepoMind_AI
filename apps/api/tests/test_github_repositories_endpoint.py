from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import pytest
from app.domain.github import GitHubTokenStatus, RepositorySummary
from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.dependencies import get_identity_provider
from app.interfaces.api.dependencies import get_github_service
from app.main import create_app
from httpx import ASGITransport, AsyncClient

from tests.test_github_service import repository_payload


class FakeIdentityProvider:
    def __init__(self, user: AuthenticatedUser | None = None) -> None:
        self.user = user or AuthenticatedUser(provider_subject="subject", email="user@example.com")

    def verify_token(self, _: str) -> AuthenticatedUser:
        return self.user


class FakeGitHubService:
    def __init__(self, repositories: list[RepositorySummary]) -> None:
        self.repositories = repositories
        self.last_kwargs: dict[str, Any] | None = None

    def get_token_status(self, _: AuthenticatedUser) -> GitHubTokenStatus:
        return GitHubTokenStatus(linked=True, token_available=True)

    def list_repositories(self, _: AuthenticatedUser, **kwargs: Any) -> list[RepositorySummary]:
        self.last_kwargs = kwargs
        return self.repositories


@asynccontextmanager
async def create_test_client(
    github_service: FakeGitHubService,
) -> AsyncIterator[AsyncClient]:
    app = create_app()
    app.dependency_overrides[get_identity_provider] = lambda: FakeIdentityProvider()
    app.dependency_overrides[get_github_service] = lambda: github_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()


def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer sample-jwt"}


@pytest.mark.asyncio
async def test_repositories_endpoint_returns_safe_repository_dtos() -> None:
    service = FakeGitHubService([RepositorySummary.from_github_api(repository_payload())])

    async with create_test_client(service) as client:
        response = await client.get("/api/v1/github/repositories", headers=auth_headers())

    assert response.status_code == 200
    payload = response.json()
    repository = payload["data"][0]
    assert repository["id"] == 123
    assert repository["name"] == "RepoMind_AI"
    assert repository["owner"]["login"] == "Karthikrnaik24"
    assert repository["language"] == "TypeScript"
    assert "node_id" not in repository
    assert "license" not in repository


@pytest.mark.asyncio
async def test_repositories_endpoint_passes_query_parameters() -> None:
    service = FakeGitHubService([])

    async with create_test_client(service) as client:
        response = await client.get(
            "/api/v1/github/repositories?page=3&per_page=25&sort=full_name"
            "&direction=asc&visibility=private&search=repo",
            headers=auth_headers(),
        )

    assert response.status_code == 200
    assert service.last_kwargs == {
        "page": 3,
        "per_page": 25,
        "sort": "full_name",
        "direction": "asc",
        "visibility": "private",
        "search": "repo",
    }
    assert response.json()["meta"]["page"] == 3


@pytest.mark.asyncio
async def test_repositories_endpoint_is_protected() -> None:
    service = FakeGitHubService([])

    async with create_test_client(service) as client:
        response = await client.get("/api/v1/github/repositories")

    assert response.status_code == 401
    assert response.json()["success"] is False