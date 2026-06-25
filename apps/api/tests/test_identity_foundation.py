from typing import Any

from app.application.services.identity_service import IdentityService
from app.domain.identity import AuthenticatedUser, IdentityProvider
from app.infrastructure.auth.supabase_provider import SupabaseIdentityProvider


class FakeIdentityProvider:
    """Test identity provider used to exercise the domain protocol."""

    def __init__(self) -> None:
        self.last_token: str | None = None

    def verify_token(self, token: str) -> AuthenticatedUser:
        self.last_token = token
        return AuthenticatedUser(
            provider_subject="provider-user-123",
            email="engineer@example.com",
            role="member",
            metadata={"source": "test"},
        )


class FakeJwtVerifier:
    """Test JWT verifier that avoids network and cryptographic dependencies."""

    def __init__(self, claims: dict[str, Any]) -> None:
        self.claims = claims
        self.last_token: str | None = None

    def verify(self, token: str) -> dict[str, Any]:
        self.last_token = token
        return self.claims


def verify_with_provider(provider: IdentityProvider, token: str) -> AuthenticatedUser:
    return provider.verify_token(token)


def test_authenticated_user_creation() -> None:
    user = AuthenticatedUser(
        provider_subject="supabase-user-123",
        email="user@example.com",
        role="admin",
        metadata={"tenant": "test"},
    )

    assert user.provider_subject == "supabase-user-123"
    assert user.email == "user@example.com"
    assert user.role == "admin"
    assert user.metadata == {"tenant": "test"}


def test_identity_provider_protocol_usage() -> None:
    provider = FakeIdentityProvider()
    sample = "sample-identity-value"

    user = verify_with_provider(provider, sample)

    assert provider.last_token == sample
    assert user.email == "engineer@example.com"


def test_supabase_identity_provider_converts_claims_to_authenticated_user() -> None:
    claims = {
        "sub": "supabase-subject-1",
        "email": "supabase@example.com",
        "role": "authenticated",
        "app_metadata": {"role": "owner"},
        "user_metadata": {"display_name": "Supabase User"},
    }
    verifier = FakeJwtVerifier(claims)
    provider = SupabaseIdentityProvider(verifier)  # type: ignore[arg-type]
    sample = "sample-jwt-value"

    user = provider.verify_token(sample)

    assert verifier.last_token == sample
    assert user.provider_subject == "supabase-subject-1"
    assert user.email == "supabase@example.com"
    assert user.role == "owner"
    assert user.metadata == {
        "app_metadata": {"role": "owner"},
        "user_metadata": {"display_name": "Supabase User"},
    }


def test_identity_service_delegates_token_verification() -> None:
    provider = FakeIdentityProvider()
    service = IdentityService(provider)
    sample = "sample-delegated-value"

    user = service.verify_token(sample)

    assert provider.last_token == sample
    assert user.provider_subject == "provider-user-123"
