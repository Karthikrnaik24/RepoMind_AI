"""GitHub application service."""

from typing import Any, Literal

from app.domain.github import GitHubTokenProvider, GitHubTokenStatus, RepositorySummary
from app.domain.identity import AuthenticatedUser
from app.infrastructure.github import GitHubClient, GitHubUnavailable

GitHubRepositorySort = Literal["created", "updated", "pushed", "full_name"]
GitHubRepositoryDirection = Literal["asc", "desc"]
GitHubRepositoryVisibility = Literal["all", "public", "private"]


class GitHubService:
    """Coordinates GitHub use cases without exposing HTTP details to routes."""

    def __init__(self, client: GitHubClient, token_provider: GitHubTokenProvider) -> None:
        self._client = client
        self._token_provider = token_provider

    def get_token_status(self, authenticated_user: AuthenticatedUser) -> GitHubTokenStatus:
        """Return safe GitHub token availability for the authenticated user."""

        return self._token_provider.get_token_status(authenticated_user)

    def list_repositories(
        self,
        authenticated_user: AuthenticatedUser,
        *,
        page: int,
        per_page: int,
        sort: GitHubRepositorySort,
        direction: GitHubRepositoryDirection,
        visibility: GitHubRepositoryVisibility,
        search: str | None = None,
    ) -> list[RepositorySummary]:
        """Fetch one page of GitHub repositories and map them into safe DTOs."""

        token = self._token_provider.get_access_token(authenticated_user)
        payload = self._client.request_json(
            "GET",
            "/user/repos",
            token=token,
            params={
                "page": page,
                "per_page": per_page,
                "sort": sort,
                "direction": direction,
                "visibility": visibility,
            },
        )
        if not isinstance(payload, list):
            raise GitHubUnavailable("GitHub returned an unexpected repository payload.")

        repositories = [
            self.to_repository_summary(item)
            for item in payload
            if isinstance(item, dict)
        ]
        if search:
            normalized_search = search.strip().lower()
            repositories = [
                repository
                for repository in repositories
                if normalized_search in repository.name.lower()
            ]
        return repositories

    def to_repository_summary(self, payload: dict[str, Any]) -> RepositorySummary:
        """Map a GitHub repository payload into a RepoMind AI DTO."""

        return RepositorySummary.from_github_api(payload)