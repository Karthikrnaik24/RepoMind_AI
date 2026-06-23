# RepoMind AI REST API Specification

## Purpose

This document defines the planned REST API for RepoMind AI. It is documentation only and does not implement routes, handlers, schemas, or client code.

The API should be stable, explicit, secure by default, and suitable for frontend, CLI, and future partner integrations.

## API Design Principles

- Use resource-oriented URLs.
- Use JSON request and response bodies.
- Use HTTPS in all deployed environments.
- Require authentication for all repository, file, search, chat, graph, architecture, and summary endpoints.
- Validate all request bodies, path parameters, and query parameters.
- Return consistent error payloads.
- Never return secrets, provider tokens, raw API keys, or sensitive internal diagnostics.
- Include pagination for list endpoints.
- Include citations for AI-generated repository claims.
- Keep long-running work asynchronous through indexing jobs.

## Base URL and Versioning

Recommended base path:

```text
/api/v1
```

Versioning rules:

- Breaking API changes require a new version prefix.
- Additive response fields are allowed within the same version.
- Deprecated fields should remain available for a documented transition period.

## Authentication Model

Primary browser authentication should use secure, HTTP-only session cookies. Programmatic access can later use API keys or OAuth application tokens.

Authentication headers:

```text
Cookie: repomind_session=<secure-session-cookie>
Authorization: Bearer <api-key-or-access-token>
```

Cookie-based sessions are preferred for the web application. Bearer tokens are reserved for future public API and CLI access.

## Standard Response Envelope

Successful responses may return either a resource object or a structured envelope. For consistency, list endpoints should use an envelope.

Single resource example:

```json
{
  "id": "repo_123",
  "name": "RepoMind_AI"
}
```

List response example:

```json
{
  "data": [],
  "pagination": {
    "limit": 25,
    "cursor": "next_cursor",
    "has_more": true
  }
}
```

## Standard Error Response

All error responses should use this shape:

```json
{
  "error": {
    "code": "repository_not_found",
    "message": "Repository was not found or you do not have access.",
    "details": {
      "repository_id": "repo_123"
    },
    "request_id": "req_abc123"
  }
}
```

Error fields:

- `code`: Stable machine-readable error code.
- `message`: Safe human-readable message.
- `details`: Optional safe structured details.
- `request_id`: Correlation ID for logs and support.

Common status codes:

- `200 OK`: Request succeeded.
- `201 Created`: Resource created.
- `202 Accepted`: Long-running job accepted.
- `204 No Content`: Request succeeded with no response body.
- `400 Bad Request`: Invalid request body or query parameters.
- `401 Unauthorized`: Missing or invalid authentication.
- `403 Forbidden`: Authenticated but not allowed to access the resource.
- `404 Not Found`: Resource not found or inaccessible.
- `409 Conflict`: Request conflicts with current state.
- `422 Unprocessable Entity`: Semantically invalid input.
- `429 Too Many Requests`: Rate limit exceeded.
- `500 Internal Server Error`: Unexpected server failure.
- `503 Service Unavailable`: Dependency unavailable or temporary outage.

Common error codes:

- `invalid_request`
- `unauthorized`
- `forbidden`
- `not_found`
- `validation_failed`
- `rate_limited`
- `provider_unavailable`
- `repository_not_found`
- `repository_access_denied`
- `indexing_job_not_found`
- `indexing_already_running`
- `file_not_found`
- `chat_session_not_found`
- `ai_provider_error`
- `insufficient_repository_context`

## Endpoint-to-Table Mapping

This section maps API capabilities to the canonical database tables defined in `docs/DATABASE.md`. Endpoint implementations should use these mappings as a starting point and should still enforce authorization before reading or writing repository-scoped data.

| API capability | Primary tables read | Primary tables written |
| --- | --- | --- |
| Login | `users`, `user_profiles` | `users`, `user_profiles`, `audit_logs` |
| Logout | `users` | `audit_logs` |
| Refresh Token | `users` | `audit_logs` |
| Profile | `users`, `user_profiles` | None |
| Connect GitHub | `users`, `repositories`, `repository_branches` | `repositories`, `repository_branches`, `indexing_jobs`, `audit_logs` |
| List repositories | `repositories`, `indexing_jobs` | None |
| Repository details | `repositories`, `repository_branches`, `indexing_jobs` | None |
| Start indexing | `repositories`, `repository_branches`, `indexing_jobs` | `indexing_jobs`, `audit_logs` |
| Index status | `indexing_jobs`, `repositories`, `repository_branches` | None |
| List files | `repositories`, `repository_branches`, `repository_files` | None |
| Read file | `repositories`, `repository_files` | None |
| Explain file | `repository_files`, `code_chunks`, `embeddings`, `dependency_edges` | None for the standalone endpoint; future persisted explanations must write through `chat_sessions`, `chat_messages`, and `citations` |
| Semantic search | `repositories`, `repository_files`, `code_chunks`, `embeddings` | None |
| Keyword search | `repositories`, `repository_files`, `code_chunks` | None |
| Create chat session | `repositories`, `repository_branches` | `chat_sessions`, `audit_logs` |
| Send message | `chat_sessions`, `repositories`, `repository_files`, `code_chunks`, `embeddings` | `chat_messages`, `citations`, `audit_logs` |
| Conversation history | `chat_sessions`, `chat_messages`, `citations`, `repository_files`, `code_chunks` | None |
| Dependency graph | `repositories`, `repository_branches`, `repository_files`, `dependency_edges` | None |
| Architecture diagram | `repositories`, `repository_branches`, `architecture_snapshots` | None |
| Repository summary | `repositories`, `repository_branches`, `architecture_snapshots`, `repository_files`, `code_chunks` | None |

API-to-database consistency rules:

- Repository-scoped endpoints must verify access through `repositories` before returning child records.
- File endpoints must only return `repository_files` that belong to the requested `repository_id`.
- Search endpoints must retrieve only `code_chunks` and `embeddings` reachable through authorized repositories and branches.
- Chat endpoints must ensure `chat_sessions.repository_id` matches the repository context used for retrieval.
- Citation responses must reference `citations`, `repository_files`, and `code_chunks`; do not introduce a separate legacy source-reference table.
- Indexing endpoints must use `indexing_jobs`; do not introduce a separate legacy analysis-job table.

## Authentication Endpoints

### Login

HTTP method: `POST`

URL: `/api/v1/auth/login`

Description: Starts an authentication flow. For GitHub OAuth, the API returns a provider authorization URL. For future email or SSO login, the response can vary by provider.

Authentication required: No.

Request body:

```json
{
  "provider": "github",
  "redirect_uri": "https://app.repomind.ai/auth/callback"
}
```

Response body:

```json
{
  "authorization_url": "https://github.com/login/oauth/authorize?...",
  "state": "opaque_csrf_state",
  "expires_at": "2026-06-23T14:30:00Z"
}
```

Status codes:

- `200 OK`: Login flow created.
- `400 Bad Request`: Unsupported provider or invalid redirect URI.
- `429 Too Many Requests`: Login attempts rate limited.

Error responses:

```json
{
  "error": {
    "code": "unsupported_auth_provider",
    "message": "The requested authentication provider is not supported.",
    "details": {
      "provider": "example"
    },
    "request_id": "req_abc123"
  }
}
```

### Logout

HTTP method: `POST`

URL: `/api/v1/auth/logout`

Description: Invalidates the current session and clears the session cookie.

Authentication required: Yes.

Request body:

```json
{}
```

Response body:

No response body.

Status codes:

- `204 No Content`: Session invalidated.
- `401 Unauthorized`: Session is missing or invalid.

Error responses:

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Authentication is required.",
    "request_id": "req_abc123"
  }
}
```

### Refresh Token

HTTP method: `POST`

URL: `/api/v1/auth/refresh`

Description: Refreshes the authenticated session. For cookie-based auth, this rotates or extends the secure session cookie. For token-based clients, this can return a new access token.

Authentication required: Yes, with a valid refresh-capable session or refresh token.

Request body:

```json
{
  "refresh_token": "optional_for_token_based_clients"
}
```

Response body:

```json
{
  "access_token": "optional_token_for_non_browser_clients",
  "token_type": "Bearer",
  "expires_at": "2026-06-23T15:00:00Z",
  "user": {
    "id": "usr_123",
    "email": "engineer@example.com"
  }
}
```

Status codes:

- `200 OK`: Session refreshed.
- `401 Unauthorized`: Refresh token or session is invalid.
- `429 Too Many Requests`: Refresh attempts rate limited.

Error responses:

```json
{
  "error": {
    "code": "invalid_refresh_token",
    "message": "The refresh token is invalid or expired.",
    "request_id": "req_abc123"
  }
}
```

### Profile

HTTP method: `GET`

URL: `/api/v1/auth/profile`

Description: Returns the authenticated user's profile and account metadata.

Authentication required: Yes.

Request body:

None.

Response body:

```json
{
  "id": "usr_123",
  "email": "engineer@example.com",
  "display_name": "Engineering Lead",
  "avatar_url": "https://avatars.githubusercontent.com/u/123",
  "timezone": "Asia/Calcutta",
  "locale": "en",
  "auth_provider": "github",
  "created_at": "2026-06-23T10:00:00Z",
  "last_login_at": "2026-06-23T13:00:00Z"
}
```

Status codes:

- `200 OK`: Profile returned.
- `401 Unauthorized`: Authentication is required.

Error responses:

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Authentication is required.",
    "request_id": "req_abc123"
  }
}
```

## Repository Endpoints

### Connect GitHub

HTTP method: `POST`

URL: `/api/v1/repositories/github/connect`

Description: Connects a GitHub repository to RepoMind AI after validating provider access. The API creates or updates the repository record but does not automatically index unless `start_indexing` is true.

Authentication required: Yes.

Request body:

```json
{
  "owner": "openai",
  "name": "example-repo",
  "provider_repository_id": "123456789",
  "default_branch": "main",
  "start_indexing": true
}
```

Response body:

```json
{
  "repository": {
    "id": "repo_123",
    "provider": "github",
    "owner_name": "openai",
    "name": "example-repo",
    "full_name": "openai/example-repo",
    "default_branch": "main",
    "visibility": "private",
    "web_url": "https://github.com/openai/example-repo",
    "last_indexed_at": null,
    "created_at": "2026-06-23T13:00:00Z"
  },
  "indexing_job": {
    "id": "job_123",
    "status": "queued"
  }
}
```

Status codes:

- `201 Created`: Repository connected.
- `200 OK`: Repository was already connected and returned.
- `202 Accepted`: Repository connected and indexing job queued.
- `400 Bad Request`: Invalid repository selection.
- `403 Forbidden`: GitHub access denied.
- `409 Conflict`: Repository already connected under conflicting ownership.
- `503 Service Unavailable`: GitHub provider unavailable.

Error responses:

```json
{
  "error": {
    "code": "repository_access_denied",
    "message": "GitHub access to this repository could not be verified.",
    "details": {
      "provider": "github",
      "owner": "openai",
      "name": "example-repo"
    },
    "request_id": "req_abc123"
  }
}
```

### List Repositories

HTTP method: `GET`

URL: `/api/v1/repositories`

Description: Lists repositories available to the authenticated user.

Authentication required: Yes.

Query parameters:

- `limit`: Optional integer from 1 to 100. Default `25`.
- `cursor`: Optional pagination cursor.
- `provider`: Optional provider filter.
- `search`: Optional repository name search.
- `indexing_status`: Optional latest indexing status filter.

Request body:

None.

Response body:

```json
{
  "data": [
    {
      "id": "repo_123",
      "provider": "github",
      "owner_name": "openai",
      "name": "example-repo",
      "full_name": "openai/example-repo",
      "default_branch": "main",
      "visibility": "private",
      "last_indexed_at": "2026-06-23T13:10:00Z",
      "latest_indexing_status": "succeeded",
      "created_at": "2026-06-23T13:00:00Z"
    }
  ],
  "pagination": {
    "limit": 25,
    "cursor": "next_cursor",
    "has_more": false
  }
}
```

Status codes:

- `200 OK`: Repositories returned.
- `400 Bad Request`: Invalid query parameters.
- `401 Unauthorized`: Authentication is required.

Error responses:

```json
{
  "error": {
    "code": "validation_failed",
    "message": "One or more query parameters are invalid.",
    "details": {
      "limit": "Must be between 1 and 100."
    },
    "request_id": "req_abc123"
  }
}
```

### Repository Details

HTTP method: `GET`

URL: `/api/v1/repositories/{repository_id}`

Description: Returns repository metadata, branch information, and latest indexing state.

Authentication required: Yes.

Request body:

None.

Response body:

```json
{
  "id": "repo_123",
  "provider": "github",
  "provider_repository_id": "123456789",
  "owner_name": "openai",
  "name": "example-repo",
  "full_name": "openai/example-repo",
  "default_branch": "main",
  "visibility": "private",
  "web_url": "https://github.com/openai/example-repo",
  "branches": [
    {
      "id": "branch_123",
      "name": "main",
      "head_commit_sha": "0123456789abcdef0123456789abcdef01234567",
      "is_default": true,
      "last_seen_at": "2026-06-23T13:00:00Z"
    }
  ],
  "latest_indexing_job": {
    "id": "job_123",
    "status": "succeeded",
    "completed_at": "2026-06-23T13:10:00Z"
  },
  "created_at": "2026-06-23T13:00:00Z",
  "updated_at": "2026-06-23T13:10:00Z"
}
```

Status codes:

- `200 OK`: Repository returned.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: Repository not found or inaccessible.

Error responses:

```json
{
  "error": {
    "code": "repository_not_found",
    "message": "Repository was not found or you do not have access.",
    "request_id": "req_abc123"
  }
}
```

### Start Indexing

HTTP method: `POST`

URL: `/api/v1/repositories/{repository_id}/index`

Description: Starts a full or incremental repository indexing job.

Authentication required: Yes.

Request body:

```json
{
  "branch": "main",
  "mode": "incremental",
  "force": false
}
```

Response body:

```json
{
  "id": "job_123",
  "repository_id": "repo_123",
  "branch": "main",
  "job_type": "incremental_index",
  "status": "queued",
  "progress_total": null,
  "progress_completed": 0,
  "created_at": "2026-06-23T13:20:00Z"
}
```

Status codes:

- `202 Accepted`: Indexing job queued.
- `400 Bad Request`: Invalid mode or branch.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: Repository or branch not found.
- `409 Conflict`: Indexing is already running.
- `429 Too Many Requests`: Indexing request rate limited.

Error responses:

```json
{
  "error": {
    "code": "indexing_already_running",
    "message": "An indexing job is already running for this repository and branch.",
    "details": {
      "indexing_job_id": "job_123"
    },
    "request_id": "req_abc123"
  }
}
```

### Index Status

HTTP method: `GET`

URL: `/api/v1/repositories/{repository_id}/index/{job_id}`

Description: Returns the status of a repository indexing job.

Authentication required: Yes.

Request body:

None.

Response body:

```json
{
  "id": "job_123",
  "repository_id": "repo_123",
  "branch": "main",
  "job_type": "incremental_index",
  "status": "running",
  "provider_commit_sha": "0123456789abcdef0123456789abcdef01234567",
  "progress_total": 1200,
  "progress_completed": 480,
  "error_code": null,
  "error_message": null,
  "created_at": "2026-06-23T13:20:00Z",
  "started_at": "2026-06-23T13:20:10Z",
  "completed_at": null
}
```

Status codes:

- `200 OK`: Job status returned.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: Repository or job not found.

Error responses:

```json
{
  "error": {
    "code": "indexing_job_not_found",
    "message": "Indexing job was not found.",
    "request_id": "req_abc123"
  }
}
```

## File Endpoints

### List Files

HTTP method: `GET`

URL: `/api/v1/repositories/{repository_id}/files`

Description: Lists indexed files for a repository and branch.

Authentication required: Yes.

Query parameters:

- `branch`: Optional branch name. Defaults to repository default branch.
- `path_prefix`: Optional folder path prefix.
- `language`: Optional language filter.
- `limit`: Optional integer from 1 to 200. Default `50`.
- `cursor`: Optional pagination cursor.

Request body:

None.

Response body:

```json
{
  "data": [
    {
      "id": "file_123",
      "path": "backend/app/main.py",
      "language": "Python",
      "size_bytes": 3200,
      "line_count": 120,
      "content_hash": "sha256_hash",
      "indexed_at": "2026-06-23T13:10:00Z"
    }
  ],
  "pagination": {
    "limit": 50,
    "cursor": "next_cursor",
    "has_more": true
  }
}
```

Status codes:

- `200 OK`: Files returned.
- `400 Bad Request`: Invalid query parameters.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: Repository or branch not found.

Error responses:

```json
{
  "error": {
    "code": "repository_not_indexed",
    "message": "Repository files are not available until indexing succeeds.",
    "request_id": "req_abc123"
  }
}
```

### Read File

HTTP method: `GET`

URL: `/api/v1/repositories/{repository_id}/files/{file_id}`

Description: Returns indexed file metadata and content when available.

Authentication required: Yes.

Query parameters:

- `include_content`: Optional boolean. Default `true`.

Request body:

None.

Response body:

```json
{
  "id": "file_123",
  "repository_id": "repo_123",
  "branch": "main",
  "path": "backend/app/main.py",
  "language": "Python",
  "mime_type": "text/x-python",
  "size_bytes": 3200,
  "line_count": 120,
  "content_hash": "sha256_hash",
  "content": "from fastapi import FastAPI\n\n...",
  "indexed_at": "2026-06-23T13:10:00Z"
}
```

Status codes:

- `200 OK`: File returned.
- `400 Bad Request`: Invalid query parameters.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: File not found or inaccessible.
- `413 Payload Too Large`: File content is too large to return.

Error responses:

```json
{
  "error": {
    "code": "file_not_found",
    "message": "File was not found or you do not have access.",
    "request_id": "req_abc123"
  }
}
```

### Explain File

HTTP method: `POST`

URL: `/api/v1/repositories/{repository_id}/files/{file_id}/explain`

Description: Generates an AI explanation of an indexed file with citations to file chunks.

Authentication required: Yes.

Request body:

```json
{
  "detail_level": "standard",
  "focus": "architecture",
  "include_dependencies": true
}
```

Response body:

```json
{
  "file_id": "file_123",
  "path": "backend/app/main.py",
  "summary": "This file initializes the backend HTTP application and registers API routes.",
  "key_responsibilities": [
    "Create the FastAPI application instance",
    "Register middleware and routers"
  ],
  "risks": [
    "Application startup configuration should avoid hardcoded secrets."
  ],
  "citations": [
    {
      "file_id": "file_123",
      "path": "backend/app/main.py",
      "start_line": 1,
      "end_line": 20,
      "chunk_id": "chunk_123"
    }
  ]
}
```

Status codes:

- `200 OK`: Explanation generated.
- `400 Bad Request`: Invalid explanation options.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: File not found.
- `422 Unprocessable Entity`: File cannot be explained.
- `503 Service Unavailable`: AI provider unavailable.

Error responses:

```json
{
  "error": {
    "code": "insufficient_repository_context",
    "message": "There is not enough indexed context to explain this file reliably.",
    "request_id": "req_abc123"
  }
}
```

## Search Endpoints

### Semantic Search

HTTP method: `POST`

URL: `/api/v1/repositories/{repository_id}/search/semantic`

Description: Searches indexed repository chunks by semantic meaning using embeddings.

Authentication required: Yes.

Request body:

```json
{
  "query": "Where is authentication handled?",
  "branch": "main",
  "limit": 10,
  "filters": {
    "languages": ["Python", "TypeScript"],
    "path_prefixes": ["backend/", "frontend/src/"],
    "chunk_types": ["code", "doc"]
  }
}
```

Response body:

```json
{
  "query": "Where is authentication handled?",
  "results": [
    {
      "chunk_id": "chunk_123",
      "file_id": "file_123",
      "path": "backend/app/auth/service.py",
      "language": "Python",
      "start_line": 10,
      "end_line": 42,
      "snippet": "class AuthService: ...",
      "score": 0.893421
    }
  ]
}
```

Status codes:

- `200 OK`: Results returned.
- `400 Bad Request`: Invalid search query or filters.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: Repository or branch not found.
- `422 Unprocessable Entity`: Repository has not been indexed.
- `503 Service Unavailable`: Embedding provider or search dependency unavailable.

Error responses:

```json
{
  "error": {
    "code": "repository_not_indexed",
    "message": "Semantic search requires a completed repository index.",
    "request_id": "req_abc123"
  }
}
```

### Keyword Search

HTTP method: `POST`

URL: `/api/v1/repositories/{repository_id}/search/keyword`

Description: Searches indexed repository files and chunks using exact, fuzzy, or full-text keyword search.

Authentication required: Yes.

Request body:

```json
{
  "query": "AuthService",
  "branch": "main",
  "limit": 25,
  "case_sensitive": false,
  "filters": {
    "languages": ["Python"],
    "path_prefixes": ["backend/"]
  }
}
```

Response body:

```json
{
  "query": "AuthService",
  "results": [
    {
      "file_id": "file_123",
      "chunk_id": "chunk_123",
      "path": "backend/app/auth/service.py",
      "language": "Python",
      "start_line": 8,
      "end_line": 24,
      "snippet": "class AuthService:",
      "match_type": "exact",
      "score": 1.0
    }
  ]
}
```

Status codes:

- `200 OK`: Results returned.
- `400 Bad Request`: Invalid query or filters.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: Repository or branch not found.
- `422 Unprocessable Entity`: Repository has not been indexed.

Error responses:

```json
{
  "error": {
    "code": "validation_failed",
    "message": "Search query must not be empty.",
    "request_id": "req_abc123"
  }
}
```

## Chat Endpoints

### Create Session

HTTP method: `POST`

URL: `/api/v1/repositories/{repository_id}/chat/sessions`

Description: Creates a chat session scoped to a repository and optional branch.

Authentication required: Yes.

Request body:

```json
{
  "branch": "main",
  "title": "Understanding authentication flow"
}
```

Response body:

```json
{
  "id": "chat_123",
  "repository_id": "repo_123",
  "branch": "main",
  "title": "Understanding authentication flow",
  "status": "active",
  "created_at": "2026-06-23T13:30:00Z",
  "updated_at": "2026-06-23T13:30:00Z"
}
```

Status codes:

- `201 Created`: Chat session created.
- `400 Bad Request`: Invalid title or branch.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: Repository or branch not found.

Error responses:

```json
{
  "error": {
    "code": "repository_not_found",
    "message": "Repository was not found or you do not have access.",
    "request_id": "req_abc123"
  }
}
```

### Send Message

HTTP method: `POST`

URL: `/api/v1/chat/sessions/{chat_session_id}/messages`

Description: Sends a user message to a repository chat session and returns the assistant response with citations.

Authentication required: Yes.

Request body:

```json
{
  "message": "How does authentication work in this repository?",
  "response_mode": "grounded",
  "max_citations": 8
}
```

Response body:

```json
{
  "user_message": {
    "id": "msg_user_123",
    "role": "user",
    "content": "How does authentication work in this repository?",
    "created_at": "2026-06-23T13:31:00Z"
  },
  "assistant_message": {
    "id": "msg_assistant_123",
    "role": "assistant",
    "content": "Authentication is handled through the auth service and route layer...",
    "model_provider": "openai",
    "model_name": "configured-model",
    "created_at": "2026-06-23T13:31:05Z",
    "citations": [
      {
        "id": "citation_123",
        "file_id": "file_123",
        "chunk_id": "chunk_123",
        "path": "backend/app/auth/service.py",
        "start_line": 10,
        "end_line": 42,
        "relevance_score": 0.91
      }
    ]
  }
}
```

Status codes:

- `200 OK`: Message processed and response returned.
- `400 Bad Request`: Invalid message.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: Chat session not found.
- `422 Unprocessable Entity`: Repository is not indexed or context is insufficient.
- `429 Too Many Requests`: Chat rate limit exceeded.
- `503 Service Unavailable`: AI provider unavailable.

Error responses:

```json
{
  "error": {
    "code": "ai_provider_error",
    "message": "The AI provider could not complete the request. Please try again.",
    "request_id": "req_abc123"
  }
}
```

### Conversation History

HTTP method: `GET`

URL: `/api/v1/chat/sessions/{chat_session_id}/messages`

Description: Returns paginated message history for a chat session.

Authentication required: Yes.

Query parameters:

- `limit`: Optional integer from 1 to 100. Default `50`.
- `cursor`: Optional pagination cursor.
- `include_citations`: Optional boolean. Default `true`.

Request body:

None.

Response body:

```json
{
  "chat_session": {
    "id": "chat_123",
    "repository_id": "repo_123",
    "title": "Understanding authentication flow",
    "status": "active"
  },
  "data": [
    {
      "id": "msg_user_123",
      "role": "user",
      "content": "How does authentication work in this repository?",
      "created_at": "2026-06-23T13:31:00Z",
      "citations": []
    },
    {
      "id": "msg_assistant_123",
      "role": "assistant",
      "content": "Authentication is handled through...",
      "created_at": "2026-06-23T13:31:05Z",
      "citations": [
        {
          "id": "citation_123",
          "path": "backend/app/auth/service.py",
          "start_line": 10,
          "end_line": 42
        }
      ]
    }
  ],
  "pagination": {
    "limit": 50,
    "cursor": "next_cursor",
    "has_more": false
  }
}
```

Status codes:

- `200 OK`: Messages returned.
- `400 Bad Request`: Invalid query parameters.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: Chat session not found.

Error responses:

```json
{
  "error": {
    "code": "chat_session_not_found",
    "message": "Chat session was not found or you do not have access.",
    "request_id": "req_abc123"
  }
}
```

## Dependency Graph Endpoint

### Get Dependency Graph

HTTP method: `GET`

URL: `/api/v1/repositories/{repository_id}/dependency-graph`

Description: Returns repository dependency graph data for visualization and impact analysis.

Authentication required: Yes.

Query parameters:

- `branch`: Optional branch name. Defaults to repository default branch.
- `scope`: Optional graph scope such as `repository`, `folder`, or `file`.
- `path`: Optional path when scope is `folder` or `file`.
- `depth`: Optional integer from 1 to 10. Default `3`.
- `include_external`: Optional boolean. Default `false`.

Request body:

None.

Response body:

```json
{
  "repository_id": "repo_123",
  "branch": "main",
  "scope": "repository",
  "nodes": [
    {
      "id": "file_123",
      "type": "file",
      "label": "backend/app/auth/service.py",
      "path": "backend/app/auth/service.py",
      "language": "Python"
    }
  ],
  "edges": [
    {
      "id": "edge_123",
      "source": "file_123",
      "target": "file_456",
      "dependency_type": "import",
      "confidence": 0.95,
      "is_external": false
    }
  ],
  "generated_at": "2026-06-23T13:40:00Z"
}
```

Status codes:

- `200 OK`: Graph returned.
- `400 Bad Request`: Invalid graph parameters.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: Repository, branch, or path not found.
- `422 Unprocessable Entity`: Dependency graph is not available yet.

Error responses:

```json
{
  "error": {
    "code": "dependency_graph_unavailable",
    "message": "Dependency graph is not available until repository analysis completes.",
    "request_id": "req_abc123"
  }
}
```

## Architecture Diagram Endpoint

### Get Architecture Diagram

HTTP method: `GET`

URL: `/api/v1/repositories/{repository_id}/architecture-diagram`

Description: Returns a generated architecture diagram for the repository. The diagram can be returned as Mermaid source plus structured nodes and edges.

Authentication required: Yes.

Query parameters:

- `branch`: Optional branch name. Defaults to repository default branch.
- `format`: Optional format, one of `mermaid`, `json`, or `both`. Default `both`.
- `snapshot_type`: Optional snapshot type such as `module_map` or `dependency_map`.

Request body:

None.

Response body:

```json
{
  "repository_id": "repo_123",
  "branch": "main",
  "snapshot_id": "snapshot_123",
  "snapshot_type": "module_map",
  "format": "both",
  "mermaid": "flowchart TB\n  Frontend --> Backend\n  Backend --> Database",
  "diagram": {
    "nodes": [
      {
        "id": "backend",
        "label": "Backend",
        "type": "service"
      }
    ],
    "edges": [
      {
        "source": "backend",
        "target": "database",
        "label": "reads and writes"
      }
    ]
  },
  "generated_at": "2026-06-23T13:45:00Z"
}
```

Status codes:

- `200 OK`: Architecture diagram returned.
- `400 Bad Request`: Invalid format or snapshot type.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: Repository or branch not found.
- `422 Unprocessable Entity`: Architecture snapshot is not available yet.

Error responses:

```json
{
  "error": {
    "code": "architecture_snapshot_unavailable",
    "message": "Architecture diagram is not available until analysis completes.",
    "request_id": "req_abc123"
  }
}
```

## Repository Summary Endpoint

### Get Repository Summary

HTTP method: `GET`

URL: `/api/v1/repositories/{repository_id}/summary`

Description: Returns an AI-generated repository summary, including purpose, structure, entry points, technologies, risks, and citations.

Authentication required: Yes.

Query parameters:

- `branch`: Optional branch name. Defaults to repository default branch.
- `detail_level`: Optional value, one of `brief`, `standard`, or `deep`. Default `standard`.
- `include_citations`: Optional boolean. Default `true`.

Request body:

None.

Response body:

```json
{
  "repository_id": "repo_123",
  "branch": "main",
  "summary": "This repository contains a web application with a React frontend and Python backend.",
  "purpose": "Repository intelligence and AI-assisted codebase exploration.",
  "technologies": [
    "TypeScript",
    "React",
    "Python",
    "FastAPI",
    "PostgreSQL"
  ],
  "entry_points": [
    {
      "path": "backend/app/main.py",
      "description": "Backend application startup."
    }
  ],
  "key_directories": [
    {
      "path": "docs/",
      "description": "Project and architecture documentation."
    }
  ],
  "risks": [
    "Authentication and repository token storage require careful security controls."
  ],
  "citations": [
    {
      "file_id": "file_123",
      "path": "docs/ARCHITECTURE.md",
      "start_line": 1,
      "end_line": 40,
      "chunk_id": "chunk_123"
    }
  ],
  "generated_at": "2026-06-23T13:50:00Z"
}
```

Status codes:

- `200 OK`: Summary returned.
- `400 Bad Request`: Invalid summary parameters.
- `401 Unauthorized`: Authentication is required.
- `403 Forbidden`: User does not have access.
- `404 Not Found`: Repository or branch not found.
- `422 Unprocessable Entity`: Repository summary is not available yet.

Error responses:

```json
{
  "error": {
    "code": "repository_summary_unavailable",
    "message": "Repository summary is not available until indexing and analysis complete.",
    "request_id": "req_abc123"
  }
}
```

## Cross-Cutting API Requirements

### Pagination

List endpoints should use cursor-based pagination.

Request parameters:

- `limit`
- `cursor`

Response fields:

- `pagination.limit`
- `pagination.cursor`
- `pagination.has_more`

### Rate Limiting

Rate limits should apply to:

- Login attempts.
- Repository indexing requests.
- Search requests.
- AI chat requests.
- API key usage.

Rate limit responses should use `429 Too Many Requests` and include safe retry metadata.

```json
{
  "error": {
    "code": "rate_limited",
    "message": "Too many requests. Please retry later.",
    "details": {
      "retry_after_seconds": 60
    },
    "request_id": "req_abc123"
  }
}
```

### Authorization

Every repository-scoped endpoint must verify:

- The user is authenticated.
- The repository exists.
- The user has access to the repository.
- The requested branch, file, chat session, or analysis artifact belongs to the repository.

### Request Validation

Validation must cover:

- UUID or public ID format.
- Pagination bounds.
- Search query length.
- Chat message length.
- Supported providers, branches, modes, formats, and detail levels.
- Maximum citation and result limits.

### Observability

Each request should produce structured logs with:

- Request ID.
- User ID when authenticated.
- Repository ID when applicable.
- Endpoint name.
- Status code.
- Latency.
- Safe error code when applicable.

AI endpoints should also record:

- Model provider.
- Model name.
- Token usage.
- Retrieval count.
- Citation count.
- Provider latency.

### Security

Security requirements:

- Do not expose provider tokens.
- Do not expose raw API keys.
- Do not include internal stack traces in API errors.
- Redact sensitive repository content from logs.
- Enforce CORS allowlists.
- Use CSRF protection for cookie-authenticated browser requests.
- Validate repository access before returning any indexed file, chunk, citation, graph, summary, or chat data.
