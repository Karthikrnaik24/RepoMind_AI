"""GitHub provider abstractions."""

from typing import Protocol

from app.domain.github.entities import GitHubTokenStatus
from app.domain.identity import AuthenticatedUser


class GitHubTokenProvider(Protocol):
    """Provides GitHub OAuth token access behind infrastructure boundaries."""

    def get_token_status(
        self,
        authenticated_user: AuthenticatedUser,
        *,
        provider_token: str | None = None,
    ) -> GitHubTokenStatus:
        """Return safe GitHub token status without exposing secret values."""

    def get_access_token(
        self,
        authenticated_user: AuthenticatedUser,
        *,
        provider_token: str | None = None,
    ) -> str:
        """Return a GitHub OAuth token for infrastructure-only API calls."""
