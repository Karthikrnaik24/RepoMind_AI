# GitHub Architecture

RepoMind AI treats GitHub as an external integration behind explicit domain,
application, and infrastructure boundaries. Sprint 3.9A creates the foundation
only: no repository listing UI, repository registration, cloning, indexing, or
AI behavior is enabled.

## Dependency Flow

```mermaid
flowchart TD
    FutureAPI["Future API Route"] --> BusinessLayer["Application / Business Layer"]
    BusinessLayer --> GitHubService["GitHubService"]
    GitHubService --> TokenProvider["GitHubTokenProvider"]
    GitHubService --> GitHubClient["GitHubClient"]
    TokenProvider --> LinkedIdentity["Linked GitHub Identity"]
    GitHubClient --> GitHubAPI["GitHub REST API"]
    GitHubClient --> GitHubErrors["Typed GitHub Exceptions"]
    GitHubService --> DTOs["Repository DTOs"]
```

## GitHub Client

`GitHubClient` is the only component allowed to perform raw GitHub HTTP
requests. It owns:

- authenticated request headers;
- timeout handling;
- retry behavior for transient failures;
- GitHub rate-limit detection;
- pagination helpers based on `Link` headers;
- typed error mapping;
- structured logging without tokens or secrets.

Application services must not import `httpx` or construct GitHub request
headers directly.

## GitHub Service

`GitHubService` is the application-facing boundary for future GitHub use cases.
It depends on `GitHubClient` and `GitHubTokenProvider`, so future routes and
business workflows do not know how tokens are retrieved or how HTTP requests are
made.

The service currently supports foundation behavior only:

- verify that a linked account token can call GitHub;
- map GitHub repository payloads into RepoMind AI repository DTOs.

## Token Provider

`GitHubTokenProvider` hides linked identity token retrieval from services.
Sprint 3.9A includes `SupabaseLinkedIdentityGitHubTokenProvider` as the adapter
boundary for linked Supabase GitHub identities.

Production token storage must be designed before repository features are built.
Provider tokens must never be logged, returned to the frontend, or stored
unencrypted.


## Token Verification Debug Flow

Sprint 3.9B adds a protected developer diagnostic endpoint:

`GET /api/v1/github/debug-token`

The endpoint returns only safe metadata:

```json
{
  "github_linked": true,
  "token_available": true,
  "provider": "github"
}
```

It must never return access tokens, refresh tokens, provider tokens, Supabase
service keys, or any other secret.

```mermaid
flowchart TD
    SupabaseIdentity["Supabase Identity"] --> AuthDependency["CurrentUser Dependency"]
    AuthDependency --> AuthenticatedUser["AuthenticatedUser Metadata"]
    AuthenticatedUser --> TokenProvider["GitHubTokenProvider"]
    TokenProvider --> SafeStatus["GitHubTokenStatus"]
    SafeStatus --> DebugEndpoint["/api/v1/github/debug-token"]
    TokenProvider -. "future infrastructure-only token use" .-> GitHubClient["GitHubClient"]
```

The dashboard shows this status only in developer mode. It displays whether the
GitHub identity is linked, whether a provider token is available, and the
provider name. It never displays token values.

## Token Verification Limitations

The backend currently authenticates requests with the Supabase JWT. Supabase
sessions can expose provider tokens to trusted client/server callback code, but
provider access tokens are not normally embedded in the JWT sent to the backend.
That means the debug endpoint can safely report `github_linked=true` while also
reporting `token_available=false` until a production token handoff/storage design
is implemented.

Before repository features are enabled, RepoMind AI must choose a secure provider
token strategy. Acceptable options include encrypted server-side token storage,
a short-lived backend token handoff during OAuth callback, or an official
Supabase-supported server flow. Tokens must remain infrastructure-only and must
not be serialized through application DTOs or frontend responses.

## DTO Mapping

GitHub JSON is normalized into RepoMind AI DTOs:

- `RepositorySummary`
- `RepositoryOwner`
- `RepositoryPermissions`
- `RepositoryLicense`
- `RepositoryLanguage`

Future API responses should expose RepoMind AI DTOs, not raw GitHub JSON.

## Error Model

GitHub failures are centralized as typed exceptions:

- `GitHubUnauthorized`
- `GitHubRateLimited`
- `GitHubNotFound`
- `GitHubUnavailable`

Future API routes should translate these through the existing standard response
envelope.

## Future Repository Features

Future repository features should follow this path:

```mermaid
sequenceDiagram
    participant Route as Future API Route
    participant Service as GitHubService
    participant TokenProvider as GitHubTokenProvider
    participant Client as GitHubClient
    participant GitHub as GitHub REST API

    Route->>Service: Request GitHub use case
    Service->>TokenProvider: Resolve linked GitHub token
    TokenProvider-->>Service: OAuth token
    Service->>Client: Execute GitHub operation
    Client->>GitHub: Authenticated REST request
    GitHub-->>Client: GitHub JSON
    Client-->>Service: Decoded payload
    Service-->>Route: RepoMind AI DTO
```

Repository listing, registration, cloning, indexing, and AI workflows must be
implemented in later sprints using this foundation.