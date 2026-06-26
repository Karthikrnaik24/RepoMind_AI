from app.domain.identity import AuthenticatedUser
from app.infrastructure.github.token_provider import SupabaseLinkedIdentityGitHubTokenProvider

SAMPLE_ACCESS_VALUE = "sample-github-access-value"


def test_token_provider_reports_linked_token_available_without_exposing_token() -> None:
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

    status = provider.get_token_status(user)

    assert status.linked is True
    assert status.token_available is True
    assert status.provider == "github"
    assert SAMPLE_ACCESS_VALUE not in repr(status)


def test_token_provider_reports_missing_token_for_linked_github_identity() -> None:
    provider = SupabaseLinkedIdentityGitHubTokenProvider()
    user = AuthenticatedUser(
        provider_subject="subject",
        email="user@example.com",
        metadata={"identities": [{"provider": "github", "identity_data": {}}]},
    )

    status = provider.get_token_status(user)

    assert status.linked is True
    assert status.token_available is False
    assert status.provider == "github"


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