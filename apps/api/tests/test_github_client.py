from __future__ import annotations

import logging
from typing import Any

import httpx
import pytest
from app.infrastructure.github import GitHubClient
from app.infrastructure.github.exceptions import GitHubRateLimited, GitHubUnauthorized


def build_client(handler: httpx.MockTransport) -> GitHubClient:
    return GitHubClient(
        base_url="https://api.github.test",
        max_retries=0,
        retry_backoff_seconds=0,
        client=httpx.Client(transport=handler, base_url="https://api.github.test"),
        logger=logging.getLogger("test.github"),
    )


def json_response(
    status_code: int,
    payload: Any,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    return httpx.Response(status_code, json=payload, headers=headers)


def test_successful_authenticated_request() -> None:
    captured_headers: httpx.Headers | None = None
    sample_access_value = "sample-github-access-value"

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_headers
        captured_headers = request.headers
        return json_response(200, {"login": "repomind"})

    client = build_client(httpx.MockTransport(handler))

    payload = client.request_json("GET", "/user", token=sample_access_value)

    assert payload == {"login": "repomind"}
    assert captured_headers is not None
    assert captured_headers["authorization"] == f"Bearer {sample_access_value}"
    assert captured_headers["accept"] == "application/vnd.github+json"


def test_unauthorized_response_maps_to_typed_exception() -> None:
    sample_access_value = "invalid-github-access-value"
    client = build_client(
        httpx.MockTransport(lambda _: json_response(401, {"message": "Bad creds"}))
    )

    with pytest.raises(GitHubUnauthorized):
        client.request_json("GET", "/user", token=sample_access_value)


def test_rate_limited_response_maps_to_typed_exception() -> None:
    sample_access_value = "sample-github-access-value"
    client = build_client(
        httpx.MockTransport(
            lambda _: json_response(
                403,
                {"message": "API rate limit exceeded"},
                {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1767225600"},
            )
        )
    )

    with pytest.raises(GitHubRateLimited) as exc_info:
        client.request_json("GET", "/user", token=sample_access_value)

    assert exc_info.value.reset_at is not None


def test_pagination_yields_items_from_all_pages() -> None:
    requests: list[str] = []
    sample_access_value = "sample-github-access-value"

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if len(requests) == 1:
            return json_response(
                200,
                [{"id": 1}],
                {"link": '<https://api.github.test/user/repos?page=2>; rel="next"'},
            )
        return json_response(200, [{"id": 2}])

    client = build_client(httpx.MockTransport(handler))

    items = list(client.paginate_json("GET", "/user/repos", token=sample_access_value))

    assert items == [{"id": 1}, {"id": 2}]
    assert requests == [
        "https://api.github.test/user/repos",
        "https://api.github.test/user/repos?page=2",
    ]