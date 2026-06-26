"""GitHub OAuth token provider adapters."""

from typing import Any

from app.domain.github import GitHubTokenProvider
from app.domain.identity import AuthenticatedUser
from app.infrastructure.github.exceptions import GitHubUnauthorized


class SupabaseLinkedIdentityGitHubTokenProvider(GitHubTokenProvider):
    """Extracts a linked GitHub OAuth token from verified identity metadata.

    The current authentication pipeline does not persist provider tokens yet.
    This adapter establishes the boundary future secure token storage or
    Supabase session refresh logic will implement without changing services.
    """

    def get_access_token(self, authenticated_user: AuthenticatedUser) -> str:
        """Return the linked GitHub OAuth token if present in metadata."""

        token = self._find_token(authenticated_user.metadata)
        if not token:
            raise GitHubUnauthorized("Linked GitHub OAuth token is unavailable.")
        return token

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