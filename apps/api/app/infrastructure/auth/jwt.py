"""Supabase JWT verification utilities.

These helpers prepare token verification infrastructure for future protected
routes. Sprint 3.1 does not attach them to route authentication.
"""

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.config.settings import Settings
from app.core.exceptions import AuthorizationException, ValidationException


@dataclass(frozen=True)
class SupabaseJwtVerifier:
    """Verify Supabase HS256 JWTs when future routes opt into authentication."""

    jwt_secret: str
    issuer: str | None = None
    audience: str | None = None

    @property
    def is_configured(self) -> bool:
        """Return whether a JWT secret is available."""

        return bool(self.jwt_secret)

    def verify(self, token: str) -> dict[str, Any]:
        """Verify a JWT signature and return claims.

        This method is intentionally unused by routes in Sprint 3.1.
        """

        if not self.jwt_secret:
            raise AuthorizationException("Supabase JWT verification is not configured.")

        header_segment, payload_segment, signature_segment = self._split_token(token)
        header = self._decode_json_segment(header_segment)
        if header.get("alg") != "HS256":
            raise AuthorizationException("Unsupported JWT signing algorithm.")

        signing_input = f"{header_segment}.{payload_segment}".encode()
        expected_signature = hmac.new(
            self.jwt_secret.encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()
        provided_signature = self._decode_segment(signature_segment)
        if not hmac.compare_digest(expected_signature, provided_signature):
            raise AuthorizationException("Invalid JWT signature.")

        claims = self._decode_json_segment(payload_segment)
        self._validate_registered_claims(claims)
        return claims

    def _validate_registered_claims(self, claims: dict[str, Any]) -> None:
        expires_at = claims.get("exp")
        if expires_at is not None and int(expires_at) < int(datetime.now(UTC).timestamp()):
            raise AuthorizationException("JWT has expired.")
        if self.issuer and claims.get("iss") != self.issuer:
            raise AuthorizationException("JWT issuer is invalid.")
        if self.audience and claims.get("aud") != self.audience:
            raise AuthorizationException("JWT audience is invalid.")

    @staticmethod
    def _split_token(token: str) -> tuple[str, str, str]:
        segments = token.split(".")
        if len(segments) != 3:
            raise ValidationException("JWT must contain header, payload, and signature.")
        return segments[0], segments[1], segments[2]

    @staticmethod
    def _decode_json_segment(segment: str) -> dict[str, Any]:
        decoded = SupabaseJwtVerifier._decode_segment(segment)
        value = json.loads(decoded)
        if not isinstance(value, dict):
            raise ValidationException("JWT segment must decode to an object.")
        return value

    @staticmethod
    def _decode_segment(segment: str) -> bytes:
        padding = "=" * (-len(segment) % 4)
        return base64.urlsafe_b64decode(f"{segment}{padding}")


def create_supabase_jwt_verifier(settings: Settings) -> SupabaseJwtVerifier:
    """Create a Supabase JWT verifier from settings."""

    issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1" if settings.supabase_url else None
    return SupabaseJwtVerifier(
        jwt_secret=settings.supabase_jwt_secret.get_secret_value(),
        issuer=issuer,
        audience="authenticated",
    )
