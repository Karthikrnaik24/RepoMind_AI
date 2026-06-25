from app.config.settings import get_settings
from app.infrastructure.auth import create_supabase_client, create_supabase_jwt_verifier
from app.infrastructure.auth.dependencies import (
    get_identity_provider,
    get_supabase_jwt_verifier,
)
from app.infrastructure.auth.supabase_provider import SupabaseIdentityProvider


def test_settings_load_supabase_configuration() -> None:
    settings = get_settings()

    assert settings.supabase_url == "https://test-project.supabase.co"
    assert settings.supabase_anon_key.get_secret_value() == "test-anon-key"
    assert settings.supabase_service_role_key.get_secret_value() == "test-service-role-key"
    assert settings.supabase_jwt_secret.get_secret_value() == "test-jwt-secret"
    assert settings.is_supabase_configured is True


def test_supabase_client_initialization_uses_settings_only() -> None:
    client = create_supabase_client(get_settings())

    assert client.url == "https://test-project.supabase.co"
    assert client.anon_key == "test-anon-key"
    assert client.service_role_key == "test-service-role-key"
    assert client.is_configured is True


def test_jwt_helper_initialization_uses_settings_only() -> None:
    verifier = create_supabase_jwt_verifier(get_settings())

    assert verifier.jwt_secret.startswith("test-jwt")
    assert verifier.issuer == "https://test-project.supabase.co/auth/v1"
    assert verifier.audience == "authenticated"
    assert verifier.is_configured is True


def test_auth_dependencies_create_identity_provider_without_route_authentication() -> None:
    verifier = get_supabase_jwt_verifier(get_settings())
    provider = get_identity_provider(verifier)

    assert verifier.is_configured is True
    assert isinstance(provider, SupabaseIdentityProvider)
