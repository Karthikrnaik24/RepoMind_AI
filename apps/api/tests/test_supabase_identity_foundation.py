from app.config.settings import get_settings
from app.infrastructure.auth import create_supabase_client, create_supabase_jwt_verifier
from app.infrastructure.auth.dependencies import (
    get_identity_provider,
    get_supabase_jwt_verifier,
)
from app.infrastructure.auth.supabase_provider import SupabaseIdentityProvider
from pytest import MonkeyPatch

TEST_SUPABASE_URL = "https://test-project.supabase.co"
DERIVED_TEST_JWKS_URL = f"{TEST_SUPABASE_URL}/auth/v1/.well-known/jwks.json"
EXPLICIT_TEST_JWKS_URL = "https://jwks.test.invalid/auth/v1/.well-known/jwks.json"


def load_isolated_settings(monkeypatch: MonkeyPatch, *, jwks_url: str = ""):
    """Load settings without allowing local .env SUPABASE_JWKS_URL to leak into tests."""

    monkeypatch.setenv("SUPABASE_URL", TEST_SUPABASE_URL)
    monkeypatch.setenv("SUPABASE_JWKS_URL", jwks_url)
    get_settings.cache_clear()
    return get_settings()


def test_settings_derives_supabase_jwks_url_when_empty(monkeypatch: MonkeyPatch) -> None:
    settings = load_isolated_settings(monkeypatch, jwks_url="")

    assert settings.supabase_url == TEST_SUPABASE_URL
    assert settings.supabase_anon_key.get_secret_value() == "test-anon-key"
    assert settings.supabase_service_role_key.get_secret_value() == "test-service-role-key"
    assert settings.supabase_jwks_url == DERIVED_TEST_JWKS_URL
    assert (
        settings.supabase_jwt_secret.get_secret_value()
        == "test-jwt-secret-with-32-bytes-minimum"
    )
    assert settings.is_supabase_configured is True


def test_settings_uses_explicit_supabase_jwks_url(monkeypatch: MonkeyPatch) -> None:
    settings = load_isolated_settings(monkeypatch, jwks_url=EXPLICIT_TEST_JWKS_URL)

    assert settings.supabase_url == TEST_SUPABASE_URL
    assert settings.supabase_jwks_url == EXPLICIT_TEST_JWKS_URL
    assert settings.is_supabase_configured is True


def test_supabase_client_initialization_uses_settings_only(monkeypatch: MonkeyPatch) -> None:
    settings = load_isolated_settings(monkeypatch, jwks_url="")
    client = create_supabase_client(settings)

    assert client.url == TEST_SUPABASE_URL
    assert client.anon_key == "test-anon-key"
    assert client.service_role_key == "test-service-role-key"
    assert client.is_configured is True


def test_jwt_helper_initialization_uses_settings_only(monkeypatch: MonkeyPatch) -> None:
    verifier = create_supabase_jwt_verifier(load_isolated_settings(monkeypatch, jwks_url=""))

    assert verifier.jwks_url == DERIVED_TEST_JWKS_URL
    assert verifier.jwt_secret.startswith("test-jwt")
    assert verifier.issuer == f"{TEST_SUPABASE_URL}/auth/v1"
    assert verifier.audience == "authenticated"
    assert verifier.is_configured is True


def test_auth_dependencies_create_identity_provider_without_route_authentication(
    monkeypatch: MonkeyPatch,
) -> None:
    settings = load_isolated_settings(monkeypatch, jwks_url="")
    verifier = get_supabase_jwt_verifier(settings)
    provider = get_identity_provider(verifier)

    assert verifier.is_configured is True
    assert isinstance(provider, SupabaseIdentityProvider)
