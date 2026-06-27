from __future__ import annotations

from typing import Any

import pytest
from app.application.services.github_service import GitHubService
from app.domain.github import GitHubTokenStatus
from app.domain.identity import AuthenticatedUser

SAMPLE_ACCESS_VALUE = "sample-github-access-value"


class FakeGitHubClient:
    def __init__(self, payload: Any | None = None) -> None:
        self.payload = payload or []
        self.last_path: str | None = None
        self.last_params: dict[str, Any] | None = None
        self.last_access_value: str | None = None

    def request_json(
        self,
        method: str,
        path: str,
        *,
        token: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        self.last_path = f"{method} {path}"
        self.last_params = params
        self.last_access_value = token
        return self.payload


class FakeTokenProvider:
    def __init__(self) -> None:
        self.last_user: AuthenticatedUser | None = None

    def get_token_status(self, user: AuthenticatedUser) -> GitHubTokenStatus:
        self.last_user = user
        return GitHubTokenStatus(linked=True, token_available=True)

    def get_access_token(self, user: AuthenticatedUser) -> str:
        self.last_user = user
        return SAMPLE_ACCESS_VALUE


def repository_payload(*, name: str = "RepoMind_AI", private: bool = True) -> dict[str, Any]:
    return {
        "id": 123,
        "node_id": "R_123",
        "name": name,
        "full_name": f"Karthikrnaik24/{name}",
        "private": private,
        "fork": False,
        "archived": False,
        "visibility": "private" if private else "public",
        "html_url": f"https://github.com/Karthikrnaik24/{name}",
        "description": "AI software engineer for GitHub repositories",
        "default_branch": "main",
        "language": "TypeScript",
        "pushed_at": "2026-06-26T10:00:00Z",
        "updated_at": "2026-06-26T11:00:00Z",
        "owner": {
            "id": 42,
            "login": "Karthikrnaik24",
            "type": "User",
            "avatar_url": "https://avatars.githubusercontent.com/u/42",
            "html_url": "https://github.com/Karthikrnaik24",
        },
        "permissions": {
            "admin": True,
            "maintain": True,
            "push": True,
            "triage": True,
            "pull": True,
        },
        "license": {
            "key": "mit",
            "name": "MIT License",
            "spdx_id": "MIT",
            "url": "https://api.github.com/licenses/mit",
        },
    }


@pytest.fixture
def authenticated_user() -> AuthenticatedUser:
    return AuthenticatedUser(provider_subject="subject", email="user@example.com")


def test_github_service_delegates_token_status_without_exposing_token(
    authenticated_user: AuthenticatedUser,
) -> None:
    provider = FakeTokenProvider()
    service = GitHubService(FakeGitHubClient(), provider)  # type: ignore[arg-type]

    status = service.get_token_status(authenticated_user)

    assert provider.last_user == authenticated_user
    assert status.linked is True
    assert status.token_available is True
    assert status.provider == "github"


def test_repository_summary_dto_mapping() -> None:
    service = GitHubService(FakeGitHubClient(), FakeTokenProvider())  # type: ignore[arg-type]

    summary = service.to_repository_summary(repository_payload())

    assert summary.github_id == 123
    assert summary.owner.login == "Karthikrnaik24"
    assert summary.permissions.admin is True
    assert summary.license is not None
    assert summary.license.spdx_id == "MIT"
    assert summary.primary_language is not None
    assert summary.primary_language.name == "TypeScript"


def test_list_repositories_uses_pagination_and_filters(
    authenticated_user: AuthenticatedUser,
) -> None:
    client = FakeGitHubClient([repository_payload(private=False)])
    service = GitHubService(client, FakeTokenProvider())  # type: ignore[arg-type]

    repositories = service.list_repositories(
        authenticated_user,
        page=2,
        per_page=50,
        sort="pushed",
        direction="asc",
        visibility="public",
    )

    assert len(repositories) == 1
    assert client.last_path == "GET /user/repos"
    assert client.last_access_value == SAMPLE_ACCESS_VALUE
    assert client.last_params == {
        "page": 2,
        "per_page": 50,
        "sort": "pushed",
        "direction": "asc",
        "visibility": "public",
    }


def test_search_repositories_uses_github_search_api(authenticated_user: AuthenticatedUser) -> None:
    client = FakeGitHubClient({"items": [repository_payload(name="RepoMind_AI", private=False)]})
    service = GitHubService(client, FakeTokenProvider())  # type: ignore[arg-type]

    repositories = service.list_repositories(
        authenticated_user,
        page=1,
        per_page=10,
        sort="updated",
        direction="desc",
        visibility="public",
        search="repomind",
    )

    assert [repository.name for repository in repositories] == ["RepoMind_AI"]
    assert client.last_path == "GET /search/repositories"
    assert client.last_params == {
        "q": "repomind in:name fork:true is:public",
        "page": 1,
        "per_page": 10,
        "sort": "updated",
        "order": "desc",
    }