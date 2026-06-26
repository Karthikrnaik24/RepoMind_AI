import pytest
from app.domain.identity import AuthenticatedUser
from app.infrastructure.github.exceptions import GitHubUnauthorized
from app.infrastructure.github.token_provider import SupabaseLinkedIdentityGitHubTokenProvider

SAMPLE_ACCESS_VALUE = "sample-github-access-value"


def test_token_provider_extracts_github_provider_token_from_metadata() -> None:
    provider = SupabaseLinkedIdentityGitHubTokenProvider()
    user = AuthenticatedUser(
        provider_subject="subject",
        email="user@example.com",
        metadata={
            "identities": [
                {"provider": "google", "identity_data": {}},
                {"provider": "github", "identity_data": {"provider_token": SAMPLE_ACCESS_VALUE}},
            ]
        },
    )

    access_value = provider.get_access_token(user)

    assert access_value == SAMPLE_ACCESS_VALUE


def test_token_provider_raises_when_github_token_is_unavailable() -> None:
    provider = SupabaseLinkedIdentityGitHubTokenProvider()
    user = AuthenticatedUser(provider_subject="subject", email="user@example.com")

    with pytest.raises(GitHubUnauthorized):
        provider.get_access_token(user)