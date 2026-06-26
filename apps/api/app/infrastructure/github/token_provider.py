"""GitHub OAuth token provider adapters."""

from typing import Any

from app.domain.github import GitHubTokenProvider, GitHubTokenStatus
from app.domain.identity import AuthenticatedUser
from app.infrastructure.github.exceptions import GitHubProviderNotLinked, GitHubTokenUnavailable


class SupabaseLinkedIdentityGitHubTokenProvider(GitHubTokenProvider):
    """Inspects and resolves linked GitHub OAuth tokens from identity metadata.

    API routes and DTOs receive only safe token status. Raw access tokens are
    returned only to infrastructure/application plumbing that immediately calls
    GitHub and must never be serialized or logged.
    """

    def get_token_status(self, authenticated_user: AuthenticatedUser) -> GitHubTokenStatus:
        """Return safe linked GitHub token status without exposing the token."""

        try:
            self.get_access_token(authenticated_user)
        except GitHubProviderNotLinked:
            return GitHubTokenStatus(linked=False, token_available=False)
        except GitHubTokenUnavailable:
            return GitHubTokenStatus(linked=True, token_available=False)

        return GitHubTokenStatus(linked=True, token_available=True)

    def get_access_token(self, authenticated_user: AuthenticatedUser) -> str:
        """Return the linked GitHub OAuth token for GitHub API calls."""

        metadata = authenticated_user.metadata
        if not self._is_github_linked(metadata):
            raise GitHubProviderNotLinked()

        token = self._find_token(metadata)
        if not token:
            raise GitHubTokenUnavailable()
        return token

    def _is_github_linked(self, metadata: dict[str, Any]) -> bool:
        providers = metadata.get("providers")
        if isinstance(providers, list) and "github" in providers:
            return True

        app_metadata = metadata.get("app_metadata")
        if isinstance(app_metadata, dict):
            app_providers = app_metadata.get("providers")
            if isinstance(app_providers, list) and "github" in app_providers:
                return True
            if app_metadata.get("provider") == "github":
                return True

        identities = metadata.get("identities")
        if not isinstance(identities, list):
            return False

        return any(
            isinstance(identity, dict) and identity.get("provider") == "github"
            for identity in identities
        )

    def _find_token(self, metadata: dict[str, Any]) -> str | None:
        token = metadata.get("github_access_token") or metadata.get("provider_token")
        if isinstance(token, str) and token.strip():
            return token

        identities = metadata.get("identities")
        if not isinstance(identities, list):
            return None

        for identity in identities:
            if not isinstance(identity, dict) or identity.get("provider") != "github":
                continue
            identity_data = identity.get("identity_data")
            if not isinstance(identity_data, dict):
                continue
            identity_token = identity_data.get("provider_token")
            if isinstance(identity_token, str) and identity_token.strip():
                return identity_token
        return None