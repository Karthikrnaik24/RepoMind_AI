"""Authentication dependency placeholders.

These providers prepare authentication wiring without implementing login, OAuth,
RBAC, user synchronization, or authentication middleware.
"""
"""Authentication dependencies for protected API routes."""

import logging
from typing import Annotated

from fastapi import Depends, Header

from app.application.services.identity_service import IdentityService
from app.config.settings import Settings, get_settings
from app.core.exceptions import AuthenticationException, AuthorizationException
from app.domain.identity import AuthenticatedUser, IdentityProvider
from app.infrastructure.auth.jwt import SupabaseJwtVerifier, create_supabase_jwt_verifier
from app.infrastructure.auth.supabase import SupabaseClient, create_supabase_client
from app.infrastructure.auth.supabase_provider import SupabaseIdentityProvider

logger = logging.getLogger(__name__)


def get_supabase_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SupabaseClient:
    """Return a configured Supabase client."""

    return create_supabase_client(settings)


def get_supabase_jwt_verifier(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SupabaseJwtVerifier:
    """Return a configured JWT verifier."""

    return create_supabase_jwt_verifier(settings)


def get_identity_provider(
    jwt_verifier: Annotated[SupabaseJwtVerifier, Depends(get_supabase_jwt_verifier)],
) -> IdentityProvider:
    """Return the configured identity provider adapter."""

    return SupabaseIdentityProvider(jwt_verifier)


def get_identity_service(
    identity_provider: Annotated[IdentityProvider, Depends(get_identity_provider)],
) -> IdentityService:
    """Return the identity service for protected route dependencies."""

    return IdentityService(identity_provider)


def extract_bearer_token(authorization: str | None) -> str:
    """Extract a bearer token from an Authorization header."""

    if not authorization:
        raise AuthenticationException(
            "Missing Authorization bearer token.",
            code="missing_token",
        )

    scheme, separator, token = authorization.partition(" ")

    if not separator or scheme.lower() != "bearer" or not token.strip():
        raise AuthenticationException(
            "Authorization header must use the Bearer scheme.",
            code="invalid_authorization_header",
        )

    return token.strip()


def get_current_user(
    identity_service: Annotated[IdentityService, Depends(get_identity_service)],
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> AuthenticatedUser:
    """Authenticate the request using an Authorization bearer token."""

    token = extract_bearer_token(authorization)

    try:
        return identity_service.verify_token(token)

    except AuthenticationException as exc:
        logger.warning(
            "JWT authentication failed",
            extra={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )
        raise

    except AuthorizationException as exc:
        logger.warning(
            "JWT authorization exception converted to authentication failure",
            extra={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )
        raise AuthenticationException(
            exc.message,
            code=exc.code,
            details=exc.details,
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected JWT verification failure")
        raise AuthenticationException(
            "Invalid JWT.",
            code="invalid_token",
        ) from exc