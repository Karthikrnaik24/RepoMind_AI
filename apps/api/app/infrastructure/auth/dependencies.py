"""Authentication dependency placeholders.

These providers prepare future authentication wiring only. They do not require
authentication and should not be used to protect routes in Sprint 3.1.
"""

from typing import Annotated, Any

from fastapi import Depends

from app.application.services.identity_service import IdentityService
from app.config.settings import Settings, get_settings
from app.domain.identity import IdentityProvider
from app.infrastructure.auth.jwt import SupabaseJwtVerifier, create_supabase_jwt_verifier
from app.infrastructure.auth.supabase import SupabaseClient, create_supabase_client
from app.infrastructure.auth.supabase_provider import SupabaseIdentityProvider


def get_supabase_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SupabaseClient:
    """Return a configured Supabase client placeholder."""

    return create_supabase_client(settings)


def get_supabase_jwt_verifier(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SupabaseJwtVerifier:
    """Return a configured JWT verifier placeholder."""

    return create_supabase_jwt_verifier(settings)


def get_identity_provider(
    jwt_verifier: Annotated[SupabaseJwtVerifier, Depends(get_supabase_jwt_verifier)],
) -> IdentityProvider:
    """Return the configured identity provider adapter."""

    return SupabaseIdentityProvider(jwt_verifier)


def get_identity_service(
    identity_provider: Annotated[IdentityProvider, Depends(get_identity_provider)],
) -> IdentityService:
    """Return the identity service without protecting any routes."""

    return IdentityService(identity_provider)


def get_current_user_placeholder() -> dict[str, Any] | None:
    """Return no authenticated user until authentication is implemented."""

    return None
