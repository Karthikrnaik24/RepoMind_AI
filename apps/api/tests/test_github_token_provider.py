import pytest
from app.domain.identity import AuthenticatedUser
from app.infrastructure.github.exceptions import (
    GitHubProviderNotLinked,
    GitHubTokenUnavailable,
)
from app.infrastructure.github.token_provider import SupabaseLinkedIdentityGitHubTokenProvider

SAMPLE_ACCESS_VALUE = "sample-github-access-value"
REQUEST_PROVIDER_TOKEN = "request-provider-token"  # noqa: S105


def github_linked_user(*, token: str | None = SAMPLE_ACCESS_VALUE) -> AuthenticatedUser:
    identity_data = {"provider_token": token} if token else {}
    return AuthenticatedUser(
        provider_subject="subject",
        email="user@example.com",
        metadata={
            "identities": [
                {"provider": "google", "identity_data": {}},
                {"provider": "github", "identity_data": identity_data},
            ]
        },
    )


def test_token_provider_reports_linked_token_available_without_exposing_token() -> None:
    provider = SupabaseLinkedIdentityGitHubTokenProvider()
    user = github_linked_user()

    status = provider.get_token_status(user)

    assert status.linked is True
    assert status.token_available is True
    assert status.provider == "github"
    assert SAMPLE_ACCESS_VALUE not in repr(status)


def test_token_provider_uses_request_provider_token_for_linked_github_identity() -> None:
    provider = SupabaseLinkedIdentityGitHubTokenProvider()
    user = github_linked_user(token=None)

    access_token = provider.get_access_token(user, provider_token=REQUEST_PROVIDER_TOKEN)
    status = provider.get_token_status(user, provider_token=REQUEST_PROVIDER_TOKEN)

    assert access_token == REQUEST_PROVIDER_TOKEN
    assert status.linked is True
    assert status.token_available is True
    assert REQUEST_PROVIDER_TOKEN not in repr(status)


def test_token_provider_reports_missing_token_for_linked_github_identity() -> None:
    provider = SupabaseLinkedIdentityGitHubTokenProvider()
    user = github_linked_user(token=None)

    status = provider.get_token_status(user)

    assert status.linked is True
    assert status.token_available is False
    assert status.provider == "github"


def test_token_provider_raises_reconnect_required_for_linked_github_without_token() -> None:
    provider = SupabaseLinkedIdentityGitHubTokenProvider()
    user = github_linked_user(token=None)

    with pytest.raises(GitHubTokenUnavailable) as exc_info:
        provider.get_access_token(user)

    assert exc_info.value.code == "github_reconnect_required"


def test_token_provider_reports_provider_not_linked() -> None:
    provider = SupabaseLinkedIdentityGitHubTokenProvider()
    user = AuthenticatedUser(
        provider_subject="subject",
        email="user@example.com",
        metadata={"identities": [{"provider": "google", "identity_data": {}}]},
    )

    status = provider.get_token_status(user)

    assert status.linked is False
    assert status.token_available is False
    assert status.provider == "github"


def test_token_provider_rejects_request_token_when_github_is_not_linked() -> None:
    provider = SupabaseLinkedIdentityGitHubTokenProvider()
    user = AuthenticatedUser(
        provider_subject="subject",
        email="user@example.com",
        metadata={"identities": [{"provider": "google", "identity_data": {}}]},
    )

    with pytest.raises(GitHubProviderNotLinked):
        provider.get_access_token(user, provider_token=REQUEST_PROVIDER_TOKEN)

