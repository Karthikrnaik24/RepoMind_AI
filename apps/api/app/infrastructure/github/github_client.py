"""Reusable GitHub HTTP client.

All GitHub HTTP behavior lives here so application services do not know about
headers, retry policy, pagination links, transport errors, or raw response
mapping.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import httpx

from app.infrastructure.github.exceptions import (
    GitHubNotFound,
    GitHubRateLimited,
    GitHubUnauthorized,
    GitHubUnavailable,
)

JsonValue = dict[str, Any] | list[Any] | None


class GitHubClient:
    """Production GitHub API client with retries and safe error mapping."""

    def __init__(
        self,
        *,
        base_url: str = "https://api.github.com",
        timeout_seconds: float = 10.0,
        max_retries: int = 2,
        retry_backoff_seconds: float = 0.25,
        client: httpx.Client | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._retry_backoff_seconds = retry_backoff_seconds
        self._client = client or httpx.Client(base_url=self._base_url, timeout=timeout_seconds)
        self._owns_client = client is None
        self._logger = logger or logging.getLogger("repomind.github")

    def close(self) -> None:
        """Close the underlying HTTP client when owned by this adapter."""

        if self._owns_client:
            self._client.close()

    def request_json(
        self,
        method: str,
        path: str,
        *,
        token: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> JsonValue:
        """Execute an authenticated GitHub request and return decoded JSON."""

        response = self._send(method, path, token=token, params=params, json=json)
        return self._decode_json(response)

    def paginate_json(
        self,
        method: str,
        path: str,
        *,
        token: str,
        params: dict[str, Any] | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Yield objects from a paginated GitHub collection endpoint."""

        next_path: str | None = path
        next_params: dict[str, Any] | None = dict(params or {})

        while next_path:
            response = self._send(method, next_path, token=token, params=next_params)
            payload = self._decode_json(response)
            if not isinstance(payload, list):
                raise GitHubUnavailable("GitHub returned an unexpected paginated payload.")

            for item in payload:
                if not isinstance(item, dict):
                    raise GitHubUnavailable("GitHub returned an unexpected paginated item.")
                yield item

            next_path = self._get_next_link(response)
            next_params = None

    def _send(
        self,
        method: str,
        path: str,
        *,
        token: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        headers = self._build_headers(token)
        request_path = self._normalize_path(path)
        last_error: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = self._client.request(
                    method,
                    request_path,
                    params=params,
                    json=json,
                    headers=headers,
                    timeout=self._timeout_seconds,
                )
                self._log_response(method, request_path, response.status_code, attempt)
                self._raise_for_status(response)
                return response
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc
                self._logger.warning(
                    "github_request_transport_error",
                    extra={"method": method, "path": request_path, "attempt": attempt},
                )
            except GitHubUnavailable as exc:
                last_error = exc
                if attempt >= self._max_retries:
                    raise
            except (GitHubUnauthorized, GitHubRateLimited, GitHubNotFound):
                raise

            if attempt < self._max_retries:
                time.sleep(self._retry_backoff_seconds * (attempt + 1))

        raise GitHubUnavailable("GitHub request failed.") from last_error

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code < 400:
            return

        if response.status_code == 401:
            raise GitHubUnauthorized()
        if self._is_rate_limited(response):
            raise GitHubRateLimited(reset_at=self._get_rate_limit_reset(response))
        if response.status_code == 404:
            raise GitHubNotFound()
        if response.status_code >= 500:
            raise GitHubUnavailable()

        raise GitHubUnavailable("GitHub returned an unexpected error.")

    @staticmethod
    def _build_headers(token: str) -> dict[str, str]:
        if not token.strip():
            raise GitHubUnauthorized("GitHub OAuth token is missing.")
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "RepoMind-AI",
        }

    @staticmethod
    def _decode_json(response: httpx.Response) -> JsonValue:
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise GitHubUnavailable("GitHub returned invalid JSON.") from exc

    @staticmethod
    def _normalize_path(path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return path if path.startswith("/") else f"/{path}"

    @staticmethod
    def _is_rate_limited(response: httpx.Response) -> bool:
        remaining = response.headers.get("x-ratelimit-remaining")
        if response.status_code == 429:
            return True
        return response.status_code == 403 and remaining == "0"

    @staticmethod
    def _get_rate_limit_reset(response: httpx.Response) -> datetime | None:
        reset_header = response.headers.get("x-ratelimit-reset")
        if not reset_header:
            return None
        try:
            return datetime.fromtimestamp(int(reset_header), tz=UTC)
        except ValueError:
            return None

    @staticmethod
    def _get_next_link(response: httpx.Response) -> str | None:
        link_header = response.headers.get("link")
        if not link_header:
            return None

        for link_part in link_header.split(","):
            link_url, separator, rel = link_part.strip().partition(";")
            if not separator or 'rel="next"' not in rel:
                continue
            return link_url.strip()[1:-1]
        return None

    def _log_response(self, method: str, path: str, status_code: int, attempt: int) -> None:
        self._logger.info(
            "github_request_completed",
            extra={"method": method, "path": path, "status_code": status_code, "attempt": attempt},
        )