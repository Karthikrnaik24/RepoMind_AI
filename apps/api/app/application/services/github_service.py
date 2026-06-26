"""GitHub application service."""

from typing import Any

from app.domain.github import GitHubTokenProvider, RepositorySummary
from app.domain.identity import AuthenticatedUser
from app.infrastructure.github import GitHubClient


class GitHubService:
    """Coordinates GitHub use cases without exposing HTTP details."""

    def __init__(self, client: GitHubClient, token_provider: GitHubTokenProvider) -> None:
        self._client = client
        self._token_provider = token_provider

    def verify_linked_account(self, authenticated_user: AuthenticatedUser) -> bool:
        """Verify that the current user has a usable linked GitHub token."""

        token = self._token_provider.get_access_token(authenticated_user)
        self._client.request_json("GET", "/user", token=token)
        return True

    def to_repository_summary(self, payload: dict[str, Any]) -> RepositorySummary:
        """Map a GitHub repository payload into a RepoMind AI DTO."""

        return RepositorySummary.from_github_api(payload)