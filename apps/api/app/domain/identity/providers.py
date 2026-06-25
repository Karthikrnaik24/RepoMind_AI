"""Identity provider interfaces."""

from typing import Protocol

from app.domain.identity.entities import AuthenticatedUser


class IdentityProvider(Protocol):
    """Interface implemented by external identity provider adapters."""

    def verify_token(self, token: str) -> AuthenticatedUser:
        """Verify an access token and return an authenticated user."""
