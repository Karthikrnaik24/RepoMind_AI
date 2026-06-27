"""Supabase JWT verification utilities.

Supabase access tokens are verified with the project's JWKS signing keys. Legacy
HS256 verification is retained only when SUPABASE_JWT_SECRET is configured.
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, ClassVar

import httpx
import jwt
from jwt.algorithms import ECAlgorithm
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError,
    InvalidTokenError,
    MissingRequiredClaimError,
    PyJWTError,
)

from app.config.settings import Settings
from app.core.exceptions import AuthenticationException

logger = logging.getLogger(__name__)

JwksFetcher = Callable[[str], dict[str, Any]]


@dataclass
class JwksCache:
    """Small in-memory JWKS cache for one Supabase JWKS URL."""

    jwks_url: str
    ttl_seconds: int = 300
    fetcher: JwksFetcher | None = None
    keys: dict[str, dict[str, Any]] = field(default_factory=dict)
    fetched_at: float = 0.0
    lock: Lock = field(default_factory=Lock)

    def get_key(self, kid: str) -> dict[str, Any] | None:
        """Return a JWK by key id, refreshing stale or missing keys."""

        with self.lock:
            if self._is_stale():
                self._refresh_locked()
            key = self.keys.get(kid)
            if key is not None:
                return key

            self._refresh_locked()
            return self.keys.get(kid)

    def _is_stale(self) -> bool:
        return not self.keys or time.time() - self.fetched_at >= self.ttl_seconds

    def _refresh_locked(self) -> None:
        try:
            jwks = self._fetch_jwks()
        except Exception as exc:
            logger.warning("jwks fetch failure", extra={"auth_event": "jwks_fetch_failure"})
            raise AuthenticationException("Invalid JWT.", code="invalid_token") from exc

        keys = jwks.get("keys")
        if not isinstance(keys, list):
            logger.warning("jwks fetch failure", extra={"auth_event": "jwks_fetch_failure"})
            raise AuthenticationException("Invalid JWT.", code="invalid_token")

        self.keys = {
            key["kid"]: key
            for key in keys
            if isinstance(key, dict) and isinstance(key.get("kid"), str)
        }
        self.fetched_at = time.time()

    def _fetch_jwks(self) -> dict[str, Any]:
        if self.fetcher is not None:
            return self.fetcher(self.jwks_url)

        with httpx.Client(timeout=5.0) as client:
            response = client.get(self.jwks_url)
            response.raise_for_status()
            return response.json()


class SupabaseJwtVerifier:
    """Verify Supabase JWTs using ES256 JWKS, with optional legacy HS256 support."""

    _shared_caches: ClassVar[dict[str, JwksCache]] = {}
    _shared_caches_lock: ClassVar[Lock] = Lock()

    def __init__(
        self,
        *,
        jwks_url: str,
        issuer: str | None = None,
        audience: str | None = None,
        jwt_secret: str = "",
        jwks_ttl_seconds: int = 300,
        jwks_fetcher: JwksFetcher | None = None,
    ) -> None:
        self.jwks_url = jwks_url
        self.issuer = issuer
        self.audience = audience
        self.jwt_secret = jwt_secret
        self.jwks_ttl_seconds = jwks_ttl_seconds
        self._jwks_fetcher = jwks_fetcher
        self._jwks_cache = self._get_or_create_cache()

    @property
    def is_configured(self) -> bool:
        """Return whether a verifier source is available."""

        return bool(self.jwks_url or self.jwt_secret)

    def verify(self, token: str) -> dict[str, Any]:
        """Verify a Supabase JWT and return claims."""

        try:
            header = jwt.get_unverified_header(token)
        except DecodeError as exc:
            raise AuthenticationException("Invalid JWT.", code="invalid_token") from exc
        except PyJWTError as exc:
            raise AuthenticationException("Invalid JWT.", code="invalid_token") from exc

        algorithm = header.get("alg")
        if algorithm == "ES256":
            return self._verify_es256(token, header)
        if algorithm == "HS256" and self.jwt_secret:
            return self._verify_hs256(token)

        raise AuthenticationException("JWT claims are invalid.", code="invalid_token_claims")

    def _verify_es256(self, token: str, header: dict[str, Any]) -> dict[str, Any]:
        kid = header.get("kid")
        if not isinstance(kid, str) or not kid:
            logger.warning("unknown kid", extra={"auth_event": "unknown_kid"})
            raise AuthenticationException("JWT claims are invalid.", code="invalid_token_claims")

        jwk = self._jwks_cache.get_key(kid)
        if jwk is None:
            logger.warning("unknown kid", extra={"auth_event": "unknown_kid"})
            raise AuthenticationException("JWT claims are invalid.", code="invalid_token_claims")

        public_key = ECAlgorithm.from_jwk(json.dumps(jwk))
        return self._decode(token, public_key, algorithms=["ES256"])

    def _verify_hs256(self, token: str) -> dict[str, Any]:
        return self._decode(token, self.jwt_secret, algorithms=["HS256"])

    def _decode(self, token: str, key: Any, *, algorithms: list[str]) -> dict[str, Any]:
        try:
            claims = jwt.decode(
                token,
                key=key,
                algorithms=algorithms,
                audience=self.audience,
                issuer=self.issuer,
                options={"require": ["exp", "iss", "aud", "sub"]},
            )
        except ExpiredSignatureError as exc:
            logger.warning("expired token", extra={"auth_event": "expired_token"})
            raise AuthenticationException("JWT has expired.", code="token_expired") from exc
        except InvalidSignatureError as exc:
            logger.warning("invalid signature", extra={"auth_event": "invalid_signature"})
            raise AuthenticationException("Invalid JWT.", code="invalid_token") from exc
        except InvalidIssuerError as exc:
            logger.warning("issuer mismatch", extra={"auth_event": "issuer_mismatch"})
            raise AuthenticationException(
                "JWT claims are invalid.",
                code="invalid_token_claims",
            ) from exc
        except InvalidAudienceError as exc:
            logger.warning("audience mismatch", extra={"auth_event": "audience_mismatch"})
            raise AuthenticationException(
                "JWT claims are invalid.",
                code="invalid_token_claims",
            ) from exc
        except MissingRequiredClaimError as exc:
            raise AuthenticationException(
                "JWT claims are invalid.",
                code="invalid_token_claims",
            ) from exc
        except DecodeError as exc:
            raise AuthenticationException("Invalid JWT.", code="invalid_token") from exc
        except InvalidTokenError as exc:
            raise AuthenticationException(
                "JWT claims are invalid.",
                code="invalid_token_claims",
            ) from exc

        if not isinstance(claims.get("sub"), str) or not claims["sub"]:
            raise AuthenticationException("JWT claims are invalid.", code="invalid_token_claims")
        return claims

    def _get_or_create_cache(self) -> JwksCache:
        if self._jwks_fetcher is not None:
            return JwksCache(
                jwks_url=self.jwks_url,
                ttl_seconds=self.jwks_ttl_seconds,
                fetcher=self._jwks_fetcher,
            )

        with self._shared_caches_lock:
            cache = self._shared_caches.get(self.jwks_url)
            if cache is None or cache.ttl_seconds != self.jwks_ttl_seconds:
                cache = JwksCache(self.jwks_url, ttl_seconds=self.jwks_ttl_seconds)
                self._shared_caches[self.jwks_url] = cache
            return cache


def create_supabase_jwt_verifier(settings: Settings) -> SupabaseJwtVerifier:
    """Create a Supabase JWT verifier from settings."""

    issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1" if settings.supabase_url else None
    return SupabaseJwtVerifier(
        jwks_url=settings.supabase_jwks_url,
        jwt_secret=settings.supabase_jwt_secret.get_secret_value(),
        issuer=issuer,
        audience="authenticated",
    )

