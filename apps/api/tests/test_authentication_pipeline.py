import base64
import hashlib
import hmac
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Any

from app.config.settings import get_settings
from app.core.exceptions import AuthenticationException
from app.domain.identity import AuthenticatedUser
from app.infrastructure.auth.dependencies import get_identity_provider
from app.main import create_app
from httpx import ASGITransport, AsyncClient


class FakeIdentityProvider:
    """Mock identity provider used by authentication pipeline tests."""

    def __init__(
        self,
        *,
        user: AuthenticatedUser | None = None,
        exception: AuthenticationException | None = None,
    ) -> None:
        self.user = user
        self.exception = exception
        self.last_token: str | None = None

    def verify_token(self, token: str) -> AuthenticatedUser:
        self.last_token = token
        if self.exception is not None:
            raise self.exception
        if self.user is None:
            raise AuthenticationException("Invalid JWT.", code="invalid_token")
        return self.user


@asynccontextmanager
async def create_test_client(
    provider: FakeIdentityProvider | None = None,
) -> AsyncIterator[AsyncClient]:
    app = create_app()
    if provider is not None:
        app.dependency_overrides[get_identity_provider] = lambda: provider
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


def create_signed_test_jwt(claims: dict[str, Any]) -> str:
    settings = get_settings()
    header = {"alg": "HS256", "typ": "JWT"}
    header_segment = encode_jwt_segment(header)
    payload_segment = encode_jwt_segment(claims)
    signing_input = f"{header_segment}.{payload_segment}".encode()
    signature = hmac.new(
        settings.supabase_jwt_secret.get_secret_value().encode(),
        signing_input,
        hashlib.sha256,
    ).digest()
    signature_segment = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    return f"{header_segment}.{payload_segment}.{signature_segment}"


def encode_jwt_segment(value: dict[str, Any]) -> str:
    payload = json.dumps(value, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(payload).rstrip(b"=").decode()


def valid_claims() -> dict[str, Any]:
    settings = get_settings()
    return {
        "aud": "authenticated",
        "email": "user@example.com",
        "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
        "iss": f"{settings.supabase_url}/auth/v1",
        "sub": "supabase-user-123",
    }


async def test_me_returns_401_when_authorization_header_is_missing() -> None:
    async with create_test_client() as client:
        response = await client.get("/api/v1/me")

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {
            "code": "missing_token",
            "message": "Missing Authorization bearer token.",
        },
    }


async def test_me_returns_401_for_invalid_bearer_format() -> None:
    async with create_test_client() as client:
        response = await client.get("/api/v1/me", headers={"Authorization": "Token abc"})

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {
            "code": "invalid_authorization_header",
            "message": "Authorization header must use the Bearer scheme.",
        },
    }


async def test_me_returns_401_for_malformed_jwt() -> None:
    async with create_test_client() as client:
        response = await client.get("/api/v1/me", headers={"Authorization": "Bearer malformed"})

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {"code": "invalid_token", "message": "Invalid JWT."},
    }


async def test_me_returns_401_for_jwt_with_invalid_structure() -> None:
    async with create_test_client() as client:
        response = await client.get("/api/v1/me", headers={"Authorization": "Bearer a.b.c.d"})

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {"code": "invalid_token", "message": "Invalid JWT."},
    }


async def test_me_returns_401_for_jwt_with_invalid_base64() -> None:
    async with create_test_client() as client:
        response = await client.get("/api/v1/me", headers={"Authorization": "Bearer %.%.%"})

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {"code": "invalid_token", "message": "Invalid JWT."},
    }


async def test_me_returns_401_for_jwt_with_invalid_json() -> None:
    invalid_json_header = base64.urlsafe_b64encode(b"not-json").rstrip(b"=").decode()
    token = f"{invalid_json_header}.e30.signature"

    async with create_test_client() as client:
        response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {"code": "invalid_token", "message": "Invalid JWT."},
    }

async def test_me_returns_401_for_invalid_jwt() -> None:
    sample = "sample-invalid-value"
    provider = FakeIdentityProvider(
        exception=AuthenticationException("Invalid JWT.", code="invalid_token"),
    )

    async with create_test_client(provider) as client:
        response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {sample}"})

    assert provider.last_token == sample
    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {
            "code": "invalid_token",
            "message": "Invalid JWT.",
        },
    }


async def test_me_returns_401_for_expired_jwt() -> None:
    claims = valid_claims()
    claims["exp"] = int((datetime.now(UTC) - timedelta(hours=1)).timestamp())
    token = create_signed_test_jwt(claims)

    async with create_test_client() as client:
        response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {
            "code": "token_expired",
            "message": "JWT has expired.",
        },
    }


async def test_me_returns_401_for_jwt_missing_subject() -> None:
    claims = valid_claims()
    claims.pop("sub")
    token = create_signed_test_jwt(claims)

    async with create_test_client() as client:
        response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {
            "code": "invalid_token_claims",
            "message": "JWT claims are invalid.",
        },
    }


async def test_me_returns_401_for_jwt_missing_email() -> None:
    claims = valid_claims()
    claims.pop("email")
    token = create_signed_test_jwt(claims)

    async with create_test_client() as client:
        response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {
            "code": "invalid_token_claims",
            "message": "JWT claims are invalid.",
        },
    }


async def test_me_returns_authenticated_user_for_valid_mocked_token() -> None:
    sample = "sample-valid-value"
    provider = FakeIdentityProvider(
        user=AuthenticatedUser(
            provider_subject="supabase-user-123",
            email="user@example.com",
            role="member",
            metadata={"team": "platform"},
        ),
    )

    async with create_test_client(provider) as client:
        response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {sample}"})

    assert provider.last_token == sample
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "id": "supabase-user-123",
            "email": "user@example.com",
            "provider": "supabase",
            "role": "member",
            "metadata": {"team": "platform"},
        },
        "meta": {},
    }

