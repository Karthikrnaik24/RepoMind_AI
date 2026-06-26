"""Supabase identity provider adapter."""

from typing import Any

from app.core.exceptions import AuthenticationException
from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.jwt import SupabaseJwtVerifier


class SupabaseIdentityProvider:
    """Convert verified Supabase JWT claims into domain identity entities."""

    def __init__(self, jwt_verifier: SupabaseJwtVerifier) -> None:
        self.jwt_verifier = jwt_verifier

    def verify_token(self, token: str) -> AuthenticatedUser:
        """Verify a Supabase JWT and return an authenticated user."""

        claims = self.jwt_verifier.verify(token)
        return self._claims_to_authenticated_user(claims)

    @staticmethod
    def _claims_to_authenticated_user(claims: dict[str, Any]) -> AuthenticatedUser:
        provider_subject = claims.get("sub")
        email = claims.get("email")
        if not isinstance(provider_subject, str) or not provider_subject:
            raise AuthenticationException("JWT claims are invalid.", code="invalid_token_claims")
        if not isinstance(email, str) or not email:
            raise AuthenticationException("JWT claims are invalid.", code="invalid_token_claims")

        app_metadata = claims.get("app_metadata")
        identities = claims.get("identities")
        providers = claims.get("providers")
        role = claims.get("role")
        if isinstance(app_metadata, dict) and isinstance(app_metadata.get("role"), str):
            role = app_metadata["role"]

        metadata: dict[str, Any] = {
            "app_metadata": app_metadata if isinstance(app_metadata, dict) else {},
            "user_metadata": claims.get("user_metadata")
            if isinstance(claims.get("user_metadata"), dict)
            else {},
        }
        if isinstance(identities, list):
            metadata["identities"] = identities
        if isinstance(providers, list):
            metadata["providers"] = providers

        return AuthenticatedUser(
            provider_subject=provider_subject,
            email=email,
            role=role if isinstance(role, str) else None,
            metadata=metadata,
        )