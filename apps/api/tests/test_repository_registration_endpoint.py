from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from app.application.services import SyncedUserIdentity
from app.core.exceptions import ResourceNotFoundException
from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.dependencies import get_identity_provider
from app.infrastructure.database.models import Repository, User, UserProfile
from app.interfaces.api.authorization import get_current_synced_user
from app.interfaces.api.dependencies import get_repository_registration_service
from app.main import create_app
from httpx import ASGITransport, AsyncClient


class FakeIdentityProvider:
    def verify_token(self, _: str) -> AuthenticatedUser:
        return AuthenticatedUser(provider_subject="supabase-user-123", email="engineer@example.com")


class FakeRegistrationService:
    def __init__(self, repository: Repository, *, not_found: bool = False) -> None:
        self.repository = repository
        self.not_found = not_found
        self.last_owner_user_id: object | None = None
        self.last_registration_input: object | None = None
        self.last_repository_id: object | None = None

    def register_repository(self, **kwargs: Any) -> Repository:
        self.last_owner_user_id = kwargs["owner_user_id"]
        self.last_registration_input = kwargs["registration_input"]
        return self.repository

    def list_registered_repositories(self, owner_user_id: object) -> list[Repository]:
        self.last_owner_user_id = owner_user_id
        return [self.repository]

    def get_registered_repository(self, **kwargs: Any) -> Repository:
        self.last_owner_user_id = kwargs["owner_user_id"]
        self.last_repository_id = kwargs["repository_id"]
        if self.not_found:
            raise ResourceNotFoundException(
                "Repository was not found.",
                code="repository_not_found",
            )
        return self.repository


def build_synced_identity() -> SyncedUserIdentity:
    user = User(
        id=uuid4(),
        email="engineer@example.com",
        auth_provider="supabase",
        auth_provider_user_id="supabase-user-123",
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    profile = UserProfile(
        id=uuid4(),
        user_id=user.id,
        display_name="Ada Engineer",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return SyncedUserIdentity(user=user, profile=profile)


def build_repository(owner_user_id: object) -> Repository:
    return Repository(
        id=uuid4(),
        owner_user_id=owner_user_id,
        provider="github",
        provider_repository_id="123",
        owner_name="Karthikrnaik24",
        name="RepoMind_AI",
        full_name="Karthikrnaik24/RepoMind_AI",
        default_branch="main",
        visibility="private",
        language="TypeScript",
        description="AI software engineer for GitHub repositories",
        web_url="https://github.com/Karthikrnaik24/RepoMind_AI",
        sync_status="PENDING",
        registered_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@asynccontextmanager
async def create_test_client(
    *,
    not_found: bool = False,
) -> AsyncIterator[tuple[AsyncClient, FakeRegistrationService]]:
    synced_identity = build_synced_identity()
    service = FakeRegistrationService(
        build_repository(synced_identity.user.id),
        not_found=not_found,
    )
    app = create_app()
    app.dependency_overrides[get_identity_provider] = lambda: FakeIdentityProvider()
    app.dependency_overrides[get_current_synced_user] = lambda: synced_identity
    app.dependency_overrides[get_repository_registration_service] = lambda: service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client, service
    finally:
        app.dependency_overrides.clear()


@asynccontextmanager
async def create_protected_test_client() -> AsyncIterator[AsyncClient]:
    service = FakeRegistrationService(build_repository(uuid4()))
    app = create_app()
    app.dependency_overrides[get_repository_registration_service] = lambda: service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()


def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer sample-jwt"}


@pytest.mark.asyncio
async def test_register_repository_endpoint_returns_registered_repository() -> None:
    async with create_test_client() as (client, service):
        response = await client.post(
            "/api/v1/repositories/register",
            json={
                "github_repository_id": "123",
                "full_name": "Karthikrnaik24/RepoMind_AI",
                "default_branch": "main",
            },
            headers=auth_headers(),
        )

    payload = response.json()
    assert response.status_code == 201
    assert payload["success"] is True
    assert payload["data"] == {
        **payload["data"],
        "github_repository_id": "123",
        "name": "RepoMind_AI",
        "full_name": "Karthikrnaik24/RepoMind_AI",
        "owner_login": "Karthikrnaik24",
        "default_branch": "main",
        "sync_status": "PENDING",
    }
    assert service.last_registration_input is not None


@pytest.mark.asyncio
async def test_list_registered_repositories_endpoint_returns_only_registered_resources() -> None:
    async with create_test_client() as (client, service):
        response = await client.get("/api/v1/repositories", headers=auth_headers())

    payload = response.json()
    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["meta"] == {"count": 1}
    assert payload["data"][0]["github_repository_id"] == "123"
    assert service.last_owner_user_id is not None


@pytest.mark.asyncio
async def test_repository_detail_endpoint_returns_registered_repository() -> None:
    async with create_test_client() as (client, service):
        response = await client.get(
            f"/api/v1/repositories/{service.repository.id}",
            headers=auth_headers(),
        )

    payload = response.json()
    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["data"] == {
        **payload["data"],
        "id": str(service.repository.id),
        "github_repository_id": "123",
        "full_name": "Karthikrnaik24/RepoMind_AI",
        "sync_status": "PENDING",
    }
    assert service.last_repository_id == service.repository.id


@pytest.mark.asyncio
async def test_repository_detail_endpoint_returns_404_for_unowned_or_missing_repository() -> None:
    async with create_test_client(not_found=True) as (client, service):
        response = await client.get(
            f"/api/v1/repositories/{service.repository.id}",
            headers=auth_headers(),
        )

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "error": {
            "code": "repository_not_found",
            "message": "Repository was not found.",
        },
    }


@pytest.mark.asyncio
async def test_register_repository_endpoint_is_protected() -> None:
    async with create_test_client() as (client, _):
        response = await client.post(
            "/api/v1/repositories/register",
            json={
                "github_repository_id": "123",
                "full_name": "Karthikrnaik24/RepoMind_AI",
                "default_branch": "main",
            },
        )

    assert response.status_code == 401
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_repository_detail_endpoint_is_protected() -> None:
    async with create_protected_test_client() as client:
        response = await client.get(f"/api/v1/repositories/{uuid4()}")

    assert response.status_code == 401
    assert response.json()["success"] is False