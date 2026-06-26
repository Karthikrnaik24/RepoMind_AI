"""GitHub provider abstractions."""

from typing import Protocol

from app.domain.github.entities import GitHubTokenStatus
from app.domain.identity import AuthenticatedUser


class GitHubTokenProvider(Protocol):
    """Provides safe GitHub OAuth token status for linked identities."""

    def get_token_status(self, authenticated_user: AuthenticatedUser) -> GitHubTokenStatus:
        """Return safe GitHub token status without exposing secret values."""