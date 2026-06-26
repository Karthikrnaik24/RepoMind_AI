"""GitHub provider abstractions."""

from typing import Protocol

from app.domain.identity import AuthenticatedUser


class GitHubTokenProvider(Protocol):
    """Provides GitHub OAuth access tokens for linked identities."""

    def get_access_token(self, authenticated_user: AuthenticatedUser) -> str:
        """Return a GitHub OAuth token for the authenticated user."""