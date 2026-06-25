"""Supabase JWT verification utilities.

These helpers prepare token verification infrastructure for protected routes
without implementing login, OAuth, or user synchronization.
"""

import base64
import binascii
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from json import JSONDecodeError
from typing import Any

from app.config.settings import Settings
from app.core.exceptions import AuthenticationException


@dataclass(frozen=True)
class SupabaseJwtVerifier:
    """Verify Supabase HS256 JWTs when routes opt into authentication."""

    jwt_secret: str
    issuer: str | None = None
    audience: str | None = None

    @property
    def is_configured(self) -> bool:
        """Return whether a JWT secret is available."""

        return bool(self.jwt_secret)

    def verify(self, token: str) -> dict[str, Any]:
        """Verify a JWT signature and return claims."""

        if not self.jwt_secret:
            raise AuthenticationException("Invalid JWT.", code="invalid_token")

        header_segment, payload_segment, signature_segment = self._split_token(token)
        header = self._decode_json_segment(header_segment)
        if header.get("alg") != "HS256":
            raise AuthenticationException("JWT claims are invalid.", code="invalid_token_claims")

        signing_input = f"{header_segment}.{payload_segment}".encode()
        expected_signature = hmac.new(
            self.jwt_secret.encode(),
            signing_input,
            hashlib.sha256,
        ).digest()
        provided_signature = self._decode_segment(signature_segment)
        if not hmac.compare_digest(expected_signature, provided_signature):
            raise AuthenticationException("Invalid JWT.", code="invalid_token")

        claims = self._decode_json_segment(payload_segment)
        self._validate_registered_claims(claims)
        return claims

    def _validate_registered_claims(self, claims: dict[str, Any]) -> None:
        expires_at = claims.get("exp")
        if expires_at is None:
            raise AuthenticationException("JWT claims are invalid.", code="invalid_token_claims")
        try:
            expires_at_timestamp = int(expires_at)
        except (TypeError, ValueError) as exc:
            raise AuthenticationException(
                "JWT claims are invalid.",
                code="invalid_token_claims",
            ) from exc
        if expires_at_timestamp < int(datetime.now(UTC).timestamp()):
            raise AuthenticationException("JWT has expired.", code="token_expired")
        if self.issuer and claims.get("iss") != self.issuer:
            raise AuthenticationException("JWT claims are invalid.", code="invalid_token_claims")
        if self.audience and claims.get("aud") != self.audience:
            raise AuthenticationException("JWT claims are invalid.", code="invalid_token_claims")

    @staticmethod
    def _split_token(token: str) -> tuple[str, str, str]:
        segments = token.split(".")
        if len(segments) != 3 or any(not segment for segment in segments):
            raise AuthenticationException("Invalid JWT.", code="invalid_token")
        return segments[0], segments[1], segments[2]

    @staticmethod
    def _decode_json_segment(segment: str) -> dict[str, Any]:
        decoded = SupabaseJwtVerifier._decode_segment(segment)
        try:
            value = json.loads(decoded)
        except (JSONDecodeError, UnicodeDecodeError) as exc:
            raise AuthenticationException("Invalid JWT.", code="invalid_token") from exc
        if not isinstance(value, dict):
            raise AuthenticationException("Invalid JWT.", code="invalid_token")
        return value

    @staticmethod
    def _decode_segment(segment: str) -> bytes:
        padding = "=" * (-len(segment) % 4)
        try:
            return base64.b64decode(f"{segment}{padding}", altchars=b"-_", validate=True)
        except (binascii.Error, ValueError) as exc:
            raise AuthenticationException("Invalid JWT.", code="invalid_token") from exc


def create_supabase_jwt_verifier(settings: Settings) -> SupabaseJwtVerifier:
    """Create a Supabase JWT verifier from settings."""

    issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1" if settings.supabase_url else None
    return SupabaseJwtVerifier(
        jwt_secret=settings.supabase_jwt_secret.get_secret_value(),
        issuer=issuer,
        audience="authenticated",
    )
