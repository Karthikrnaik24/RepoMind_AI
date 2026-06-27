import base64
import hashlib
import hmac
import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import pytest
from app.core.exceptions import AuthenticationException
from app.infrastructure.auth.jwt import SupabaseJwtVerifier
from cryptography.hazmat.primitives.asymmetric import ec

ISSUER = "https://test-project.supabase.co/auth/v1"
AUDIENCE = "authenticated"
JWKS_URL = "https://test-project.supabase.co/auth/v1/.well-known/jwks.json"


def base64url_uint(value: int, length: int = 32) -> str:
    raw = value.to_bytes(length, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def create_key_pair(kid: str = "test-key") -> tuple[ec.EllipticCurvePrivateKey, dict[str, Any]]:
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_numbers = private_key.public_key().public_numbers()
    jwk = {
        "kty": "EC",
        "use": "sig",
        "kid": kid,
        "alg": "ES256",
        "crv": "P-256",
        "x": base64url_uint(public_numbers.x),
        "y": base64url_uint(public_numbers.y),
    }
    return private_key, jwk


def valid_claims() -> dict[str, Any]:
    return {
        "aud": AUDIENCE,
        "email": "engineer@example.com",
        "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
        "iss": ISSUER,
        "sub": "supabase-user-123",
    }


def sign_es256_token(
    private_key: ec.EllipticCurvePrivateKey,
    claims: dict[str, Any] | None = None,
    *,
    kid: str = "test-key",
) -> str:
    return jwt.encode(
        claims or valid_claims(),
        private_key,
        algorithm="ES256",
        headers={"kid": kid},
    )


def sign_hs256_token(claims: dict[str, Any], secret: str) -> str:
    header_segment = encode_segment({"alg": "HS256", "typ": "JWT"})
    payload_segment = encode_segment(claims)
    signing_input = f"{header_segment}.{payload_segment}".encode()
    signature = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    signature_segment = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    return f"{header_segment}.{payload_segment}.{signature_segment}"


def encode_segment(value: dict[str, Any]) -> str:
    return base64.urlsafe_b64encode(
        json.dumps(value, separators=(",", ":")).encode(),
    ).rstrip(b"=").decode()


def create_verifier(
    jwks: dict[str, Any],
    *,
    jwt_secret: str = "",
) -> tuple[SupabaseJwtVerifier, list[str]]:
    calls: list[str] = []

    def fetcher(url: str) -> dict[str, Any]:
        calls.append(url)
        return jwks

    verifier = SupabaseJwtVerifier(
        jwks_url=JWKS_URL,
        jwt_secret=jwt_secret,
        issuer=ISSUER,
        audience=AUDIENCE,
        jwks_fetcher=fetcher,
    )
    return verifier, calls


def test_es256_token_is_verified_with_matching_jwks_key() -> None:
    private_key, jwk = create_key_pair()
    verifier, calls = create_verifier({"keys": [jwk]})

    claims = verifier.verify(sign_es256_token(private_key))

    assert claims["sub"] == "supabase-user-123"
    assert calls == [JWKS_URL]


def test_jwks_cache_is_reused_for_same_kid() -> None:
    private_key, jwk = create_key_pair()
    verifier, calls = create_verifier({"keys": [jwk]})

    verifier.verify(sign_es256_token(private_key))
    verifier.verify(sign_es256_token(private_key))

    assert calls == [JWKS_URL]


def test_unknown_kid_refreshes_jwks_and_returns_401(caplog: pytest.LogCaptureFixture) -> None:
    private_key, jwk = create_key_pair("known-key")
    verifier, calls = create_verifier({"keys": [jwk]})

    with caplog.at_level(logging.WARNING):
        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(sign_es256_token(private_key, kid="unknown-key"))

    assert exc_info.value.code == "invalid_token_claims"
    assert calls == [JWKS_URL, JWKS_URL]
    assert "unknown kid" in caplog.text


def test_invalid_es256_signature_returns_invalid_token(
    caplog: pytest.LogCaptureFixture,
) -> None:
    private_key, _ = create_key_pair()
    _, jwk = create_key_pair()
    verifier, _ = create_verifier({"keys": [jwk]})

    with caplog.at_level(logging.WARNING):
        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(sign_es256_token(private_key))

    assert exc_info.value.code == "invalid_token"
    assert "invalid signature" in caplog.text


def test_expired_es256_token_returns_token_expired(caplog: pytest.LogCaptureFixture) -> None:
    private_key, jwk = create_key_pair()
    claims = valid_claims()
    claims["exp"] = int((datetime.now(UTC) - timedelta(minutes=1)).timestamp())
    verifier, _ = create_verifier({"keys": [jwk]})

    with caplog.at_level(logging.WARNING):
        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(sign_es256_token(private_key, claims))

    assert exc_info.value.code == "token_expired"
    assert "expired token" in caplog.text


def test_issuer_mismatch_returns_invalid_claims(caplog: pytest.LogCaptureFixture) -> None:
    private_key, jwk = create_key_pair()
    claims = valid_claims()
    claims["iss"] = "https://other.supabase.co/auth/v1"
    verifier, _ = create_verifier({"keys": [jwk]})

    with caplog.at_level(logging.WARNING):
        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(sign_es256_token(private_key, claims))

    assert exc_info.value.code == "invalid_token_claims"
    assert "issuer mismatch" in caplog.text


def test_audience_mismatch_returns_invalid_claims(caplog: pytest.LogCaptureFixture) -> None:
    private_key, jwk = create_key_pair()
    claims = valid_claims()
    claims["aud"] = "anon"
    verifier, _ = create_verifier({"keys": [jwk]})

    with caplog.at_level(logging.WARNING):
        with pytest.raises(AuthenticationException) as exc_info:
            verifier.verify(sign_es256_token(private_key, claims))

    assert exc_info.value.code == "invalid_token_claims"
    assert "audience mismatch" in caplog.text


def test_hs256_token_is_supported_only_when_secret_exists() -> None:
    legacy_key = "legacy-hs256-key-with-32-bytes-minimum"
    token = sign_hs256_token(valid_claims(), legacy_key)
    verifier, _ = create_verifier({"keys": []}, jwt_secret=legacy_key)

    claims = verifier.verify(token)

    assert claims["sub"] == "supabase-user-123"


def test_hs256_token_without_secret_is_rejected() -> None:
    token = sign_hs256_token(valid_claims(), "legacy-hs256-key-with-32-bytes-minimum")
    verifier, _ = create_verifier({"keys": []})

    with pytest.raises(AuthenticationException) as exc_info:
        verifier.verify(token)

    assert exc_info.value.code == "invalid_token_claims"



