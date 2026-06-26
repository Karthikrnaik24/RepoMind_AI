from __future__ import annotations

from typing import Any

from app.application.services.github_service import GitHubService
from app.domain.identity import AuthenticatedUser

SAMPLE_ACCESS_VALUE = "sample-github-access-value"


class FakeGitHubClient:
    def __init__(self) -> None:
        self.last_access_value: str | None = None
        self.last_path: str | None = None

    def request_json(self, method: str, path: str, *, token: str) -> dict[str, str]:
        self.last_access_value = token
        self.last_path = f"{method} {path}"
        return {"login": "repomind"}


class FakeTokenProvider:
    def get_access_token(self, _: AuthenticatedUser) -> str:
        return SAMPLE_ACCESS_VALUE


def repository_payload() -> dict[str, Any]:
    return {
        "id": 123,
        "node_id": "R_123",
        "name": "RepoMind_AI",
        "full_name": "Karthikrnaik24/RepoMind_AI",
        "private": True,
        "fork": False,
        "archived": False,
        "visibility": "private",
        "html_url": "https://github.com/Karthikrnaik24/RepoMind_AI",
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


def test_github_service_uses_token_provider_and_client() -> None:
    client = FakeGitHubClient()
    service = GitHubService(client, FakeTokenProvider())  # type: ignore[arg-type]
    user = AuthenticatedUser(provider_subject="subject", email="user@example.com")

    assert service.verify_linked_account(user) is True
    assert client.last_access_value == SAMPLE_ACCESS_VALUE
    assert client.last_path == "GET /user"


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