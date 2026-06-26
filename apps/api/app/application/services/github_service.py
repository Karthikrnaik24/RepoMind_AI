"""GitHub application service."""

from typing import Any

from app.domain.github import GitHubTokenProvider, GitHubTokenStatus, RepositorySummary
from app.domain.identity import AuthenticatedUser
from app.infrastructure.github import GitHubClient


class GitHubService:
    """Coordinates GitHub use cases without exposing HTTP details or tokens."""

    def __init__(self, client: GitHubClient, token_provider: GitHubTokenProvider) -> None:
        self._client = client
        self._token_provider = token_provider

    def get_token_status(self, authenticated_user: AuthenticatedUser) -> GitHubTokenStatus:
        """Return safe GitHub token availability for the authenticated user."""

        return self._token_provider.get_token_status(authenticated_user)

    def to_repository_summary(self, payload: dict[str, Any]) -> RepositorySummary:
        """Map a GitHub repository payload into a RepoMind AI DTO."""

        return RepositorySummary.from_github_api(payload)