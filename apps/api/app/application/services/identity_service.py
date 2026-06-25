"""Identity application service."""

from app.domain.identity import AuthenticatedUser, IdentityProvider


class IdentityService:
    """Coordinates token verification through an injected identity provider."""

    def __init__(self, identity_provider: IdentityProvider) -> None:
        self.identity_provider = identity_provider

    def verify_token(self, token: str) -> AuthenticatedUser:
        """Verify a token and return the authenticated user."""

        return self.identity_provider.verify_token(token)
