# RepoMind AI Architecture

## Purpose

This document defines the foundational architecture for RepoMind AI. It is intended to guide implementation before application code is introduced.

RepoMind AI should be designed as a production-grade system that can grow from an MVP into a scalable repository intelligence platform for many users, teams, and repositories.

## Architecture Assumptions

Initial assumptions:

- The frontend will be a TypeScript React application.
- The backend will be a Python FastAPI application.
- PostgreSQL will be the primary relational database.
- Vector search will initially use `pgvector`, with the option to move to a dedicated vector store later.
- Redis will support background job coordination, caching, and rate limiting.
- Repository analysis and AI workflows will run through asynchronous background jobs where appropriate.
- GitHub will be the first repository provider integration.
- AI providers will be accessed through internal provider interfaces, not directly throughout the codebase.
- Secrets, tokens, and model configuration will be provided through environment variables or managed secret storage.

These assumptions should be revisited through architecture decision records as implementation progresses.

## 1. Overall System Architecture

RepoMind AI uses a modular client-server architecture with clear boundaries between the user interface, application services, domain logic, infrastructure adapters, data storage, and external providers.

```mermaid
flowchart TB
    User["User"] --> Browser["Frontend Web App"]
    Browser --> API["Backend API"]

    API --> Auth["Auth Module"]
    API --> RepoApp["Repository Application Services"]
    API --> ChatApp["AI Chat Application Services"]
    API --> AdminApp["Workspace and Admin Services"]

    RepoApp --> Jobs["Background Job Queue"]
    ChatApp --> Retrieval["Retrieval Service"]
    ChatApp --> AIOrchestrator["AI Orchestration Service"]

    Jobs --> Workers["Worker Processes"]
    Workers --> Indexing["Repository Indexing Pipeline"]
    Workers --> Summaries["Summary Generation Pipeline"]

    Indexing --> GitHub["GitHub API"]
    Indexing --> Database["PostgreSQL and pgvector"]
    Retrieval --> Database
    API --> Database

    AIOrchestrator --> AIProvider["AI Provider"]
    Auth --> OAuthProvider["OAuth Provider"]

    API --> Observability["Logs, Metrics, Traces"]
    Workers --> Observability
```

Primary responsibilities:

- Frontend: Presents repository intelligence workflows, authentication state, analysis progress, and chat experiences.
- Backend API: Validates requests, enforces authorization, coordinates use cases, and exposes product capabilities.
- Application services: Implement use cases without depending directly on frameworks or external providers.
- Background workers: Execute long-running repository ingestion, indexing, embedding, and summarization tasks.
- Database: Stores users, profiles, repositories, branches, indexing metadata, files, code chunks, embeddings, chat sessions, chat messages, citations, dependency edges, architecture snapshots, API keys, and audit logs.
- AI orchestration: Coordinates retrieval, prompt construction, model calls, response validation, and citation handling.
- Provider adapters: Integrate with GitHub, AI providers, storage, email, observability, and deployment infrastructure.

## 2. Frontend Architecture

The frontend should be organized around product workflows rather than technical concerns alone. Shared UI components should remain reusable, while repository-specific logic should live in feature modules.

```mermaid
flowchart LR
    App["App Shell and Routing"] --> Pages["Pages"]
    Pages --> Features["Feature Modules"]
    Features --> Components["Shared Components"]
    Features --> Hooks["Feature Hooks"]
    Features --> APIClient["Typed API Client"]
    APIClient --> Backend["Backend API"]

    App --> AuthState["Auth State Provider"]
    App --> QueryClient["Server State Cache"]
    App --> DesignSystem["Design System"]
```

Recommended structure:

```text
frontend/
  src/
    app/
    api/
    components/
    features/
      auth/
      repositories/
      indexing/
      chat/
      workspace/
    hooks/
    lib/
    styles/
    types/
```

Frontend principles:

- Keep API access centralized behind typed clients.
- Use server-state tools for fetching, caching, invalidation, and polling indexing jobs.
- Keep forms validated at the browser boundary before calling backend APIs.
- Keep authentication state explicit and recoverable after refresh.
- Avoid putting business rules directly inside presentational components.
- Keep repository analysis status visible for long-running workflows.
- Never expose API keys, provider tokens, or internal secrets in browser code.

Core frontend feature areas:

- Authentication and session handling.
- Repository connection and selection.
- Repository analysis status.
- Repository overview and generated documentation.
- AI chat with citations.
- User feedback on answer quality.
- Workspace and account settings.

## 3. Backend Architecture

The backend follows Clean Architecture. Framework code should remain at the edges, while business use cases live in application services and core rules live in domain modules.

```mermaid
flowchart TB
    Interfaces["Interfaces Layer\nHTTP routes, schemas, CLI adapters"] --> Application["Application Layer\nUse cases, commands, queries"]
    Application --> Domain["Domain Layer\nEntities, value objects, policies, ports"]
    Application --> Ports["Application Ports\nRepositories, providers, queues"]
    Infrastructure["Infrastructure Layer\nDB, GitHub, AI, Redis, storage"] --> Ports
    Infrastructure --> Domain
```

Recommended structure:

```text
backend/
  app/
    domain/
      repositories/
      users/
      organizations/
      conversations/
      indexing/
    application/
      repositories/
      indexing/
      chat/
      auth/
    infrastructure/
      persistence/
      github/
      ai/
      queue/
      storage/
      observability/
    interfaces/
      http/
      workers/
    config/
    shared/
  tests/
```

Backend principles:

- HTTP routes should validate input, call application services, and shape responses.
- Application services should orchestrate use cases and depend on interfaces.
- Domain models should not import FastAPI, SQLAlchemy, Redis, GitHub SDKs, or AI SDKs.
- Infrastructure adapters should implement defined ports.
- Background workers should call application services instead of duplicating business logic.
- Errors should be structured and mapped to safe API responses.
- Logs should include correlation IDs and operational context without exposing secrets.

Key backend modules:

- Auth service: Session management, OAuth callbacks, token storage coordination, and access checks.
- Repository service: Repository records, provider connections, permissions, and metadata.
- Indexing service: Repository ingestion, chunking, embedding, and indexing job orchestration.
- Retrieval service: Context search for AI workflows.
- AI chat service: Prompt assembly, model call orchestration, response validation, and citation handling.
- Audit service: Security-relevant and user-visible activity records.

## 4. Database Architecture

PostgreSQL is the primary system of record. `pgvector` can be used initially for embeddings to reduce infrastructure complexity.

```mermaid
erDiagram
    users ||--o| user_profiles : has
    users ||--o{ repositories : owns
    users ||--o{ api_keys : creates
    users ||--o{ audit_logs : triggers
    users ||--o{ chat_sessions : starts

    repositories ||--o{ repository_branches : has
    repositories ||--o{ repository_files : contains
    repositories ||--o{ indexing_jobs : indexes
    repositories ||--o{ chat_sessions : discussed_in
    repositories ||--o{ dependency_edges : maps
    repositories ||--o{ architecture_snapshots : summarizes
    repositories ||--o{ audit_logs : referenced_by

    repository_branches ||--o{ repository_files : includes
    repository_branches ||--o{ indexing_jobs : targets

    repository_files ||--o{ code_chunks : split_into
    repository_files ||--o{ dependency_edges : source_file
    repository_files ||--o{ dependency_edges : target_file

    code_chunks ||--o{ embeddings : embedded_as
    code_chunks ||--o{ citations : cited_by

    indexing_jobs ||--o{ repository_files : discovers
    indexing_jobs ||--o{ code_chunks : produces
    indexing_jobs ||--o{ embeddings : produces
    indexing_jobs ||--o{ architecture_snapshots : produces

    chat_sessions ||--o{ chat_messages : contains
    chat_messages ||--o{ citations : cites

    users {
        uuid id
        string email
        string auth_provider
        string auth_provider_user_id
        string status
        datetime created_at
        datetime updated_at
    }

    user_profiles {
        uuid id
        uuid user_id
        string display_name
        string avatar_url
        string timezone
        datetime created_at
        datetime updated_at
    }

    repositories {
        uuid id
        uuid owner_user_id
        string provider
        string provider_repository_id
        string owner_name
        string name
        string default_branch
        string visibility
        datetime created_at
        datetime updated_at
    }

    repository_branches {
        uuid id
        uuid repository_id
        string name
        string head_commit_sha
        boolean is_default
        datetime last_seen_at
    }

    repository_files {
        uuid id
        uuid repository_id
        uuid branch_id
        uuid indexing_job_id
        string path
        string language
        string content_hash
        int size_bytes
        datetime indexed_at
    }

    code_chunks {
        uuid id
        uuid repository_file_id
        uuid indexing_job_id
        int chunk_index
        text content
        string content_hash
    }

    embeddings {
        uuid id
        uuid code_chunk_id
        uuid indexing_job_id
        string model_name
        vector embedding
        datetime created_at
    }

    indexing_jobs {
        uuid id
        uuid repository_id
        uuid branch_id
        uuid requested_by_user_id
        string status
        string job_type
        datetime started_at
        datetime completed_at
    }

    chat_sessions {
        uuid id
        uuid repository_id
        uuid user_id
        uuid branch_id
        string title
        datetime created_at
    }

    chat_messages {
        uuid id
        uuid chat_session_id
        string role
        text content
        string model_name
        datetime created_at
    }

    citations {
        uuid id
        uuid chat_message_id
        uuid code_chunk_id
        uuid repository_file_id
        uuid repository_id
        int start_line
        int end_line
    }

    dependency_edges {
        uuid id
        uuid repository_id
        uuid source_file_id
        uuid target_file_id
        string dependency_type
        datetime created_at
    }

    architecture_snapshots {
        uuid id
        uuid repository_id
        uuid indexing_job_id
        string snapshot_type
        jsonb content
    }

    api_keys {
        uuid id
        uuid user_id
        string key_hash
        string status
        datetime created_at
    }

    audit_logs {
        uuid id
        uuid user_id
        uuid repository_id
        string action
        string resource_type
        datetime created_at
    }
```

Database design principles:

- Use UUID primary keys for externally referenced product entities.
- Store provider identifiers separately from internal IDs.
- Store enough metadata to support re-indexing and auditability.
- Keep embeddings linked to specific chunks, models, and timestamps.
- Avoid storing raw access tokens without encryption.
- Use migrations for all schema changes.
- Add indexes for high-frequency lookup paths such as user ID, repository ID, branch ID, indexing job status, file path, chat session ID, citation lookup, and vector search.

## 5. Authentication Flow

Authentication should support secure user sessions and future team-based access control. GitHub OAuth can serve both authentication and repository authorization, but those concepts should remain separate in the architecture.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant OAuth as OAuth Provider
    participant DB as Database

    User->>Frontend: Click sign in
    Frontend->>Backend: Request OAuth login URL
    Backend->>OAuth: Create authorization request
    OAuth-->>Frontend: Redirect user to provider
    User->>OAuth: Authorize application
    OAuth->>Backend: Callback with authorization code
    Backend->>OAuth: Exchange code for tokens
    Backend->>DB: Upsert user and store encrypted token metadata
    Backend-->>Frontend: Set secure session cookie
    Frontend->>Backend: Request current user
    Backend-->>Frontend: Return authenticated user context
```

Authentication requirements:

- Use secure, HTTP-only cookies for browser sessions where possible.
- Separate identity authentication from repository provider authorization.
- Encrypt provider tokens at rest.
- Store token scopes and expiration metadata.
- Support token revocation and account disconnection.
- Apply CSRF protection for cookie-based sessions.
- Enforce organization and repository authorization on every protected backend request.

## 6. GitHub Integration Flow

GitHub integration should be implemented through a provider abstraction so GitLab, Bitbucket, and self-hosted providers can be added later.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant GitHub
    participant Queue
    participant Worker
    participant DB

    User->>Frontend: Connect GitHub repository
    Frontend->>Backend: Submit repository selection
    Backend->>DB: Validate user and provider connection
    Backend->>GitHub: Verify repository access
    GitHub-->>Backend: Repository metadata
    Backend->>DB: Create or update repository record
    Backend->>Queue: Enqueue repository indexing job
    Backend-->>Frontend: Return repository and job status
    Queue->>Worker: Dispatch indexing job
    Worker->>GitHub: Fetch repository tree and content
    Worker->>DB: Persist files, metadata, chunks, embeddings, and job status
```

GitHub integration requirements:

- Request the minimum required OAuth scopes.
- Validate repository ownership and access before indexing.
- Respect provider rate limits.
- Handle private repositories as sensitive data.
- Avoid logging full source content or tokens.
- Store provider IDs and installation metadata for reliable synchronization.
- Support re-indexing when repository content changes.

Future GitHub capabilities:

- GitHub App installation flow.
- Webhooks for push and pull request events.
- Pull request impact analysis.
- Inline review comments where explicitly enabled.
- Organization-level repository discovery.

## 7. Repository Indexing Pipeline

Repository indexing converts repository content into structured metadata, searchable code chunks, embeddings, summaries, dependency edges, architecture snapshots, and citation-ready file references.

```mermaid
flowchart TB
    Start["Indexing Job Created"] --> Access["Validate Repository Access"]
    Access --> FetchTree["Fetch Repository Tree"]
    FetchTree --> Filter["Apply Ignore Rules and Size Limits"]
    Filter --> Detect["Detect Languages and Frameworks"]
    Detect --> FetchFiles["Fetch Eligible File Content"]
    FetchFiles --> Hash["Compute Content Hashes"]
    Hash --> Changed{"File Changed?"}
    Changed -- "No" --> Reuse["Reuse Existing Chunks and Embeddings"]
    Changed -- "Yes" --> Parse["Parse and Normalize Content"]
    Parse --> Chunk["Create Searchable Chunks"]
    Chunk --> Embed["Generate Embeddings"]
    Embed --> Persist["Persist Metadata, Chunks, and Embeddings"]
    Reuse --> Persist
    Persist --> Summarize["Generate Repository and Folder Summaries"]
    Summarize --> Complete["Mark Job Complete"]

    Access --> Failed["Mark Job Failed"]
    FetchTree --> Failed
    FetchFiles --> Failed
    Embed --> Failed
```

Indexing stages:

- Access validation: Confirm the user or organization can index the repository.
- Tree fetch: Retrieve repository paths, file sizes, commit metadata, and branch details.
- Filtering: Exclude ignored folders, generated files, binary files, large files, secrets, and unsupported file types.
- Language detection: Identify languages and frameworks for better chunking and summaries.
- Content hashing: Detect unchanged files and avoid unnecessary reprocessing.
- Chunking: Split files into meaningful units with stable references.
- Embedding: Convert chunks into vector representations for retrieval.
- Summarization: Generate repository, folder, and file-level summaries where useful.
- Persistence: Store repository metadata, repository_files, code_chunks, embeddings, dependency_edges, architecture_snapshots, and indexing job status transactionally where practical.

Indexing safeguards:

- Repository size limits.
- File size limits.
- Binary file detection.
- Timeout and retry policy.
- Provider rate limit handling.
- Sensitive file detection.
- Idempotent job behavior.

## 8. RAG Pipeline

Retrieval-augmented generation grounds AI responses in repository-specific context.

```mermaid
flowchart LR
    UserQuestion["User Question"] --> Normalize["Normalize and Validate Query"]
    Normalize --> Intent["Classify Intent"]
    Intent --> Retrieve["Retrieve Relevant Chunks"]
    Retrieve --> Rerank["Rerank and Filter Context"]
    Rerank --> BuildPrompt["Build Prompt with Sources"]
    BuildPrompt --> Model["Call AI Model"]
    Model --> Validate["Validate Grounding and Citations"]
    Validate --> Response["Return Answer with Source References"]
```

RAG requirements:

- Retrieve context only from repositories the user is authorized to access.
- Include file paths, line ranges, commit metadata, and chunk identifiers where available.
- Prefer hybrid retrieval when keyword matching is important for symbols, filenames, and exact error messages.
- Rerank results before prompt assembly when context volume is high.
- Keep prompt templates versioned and reviewable.
- Require citations for repository-specific claims.
- Clearly state uncertainty when retrieved context is insufficient.

Quality controls:

- Retrieval evaluation sets.
- Prompt regression tests.
- Citation validation.
- Token budget controls.
- Model fallback behavior.
- User feedback capture.

## 9. AI Chat Flow

AI chat should feel conversational while remaining grounded, auditable, and safe.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Retrieval
    participant AI
    participant DB

    User->>Frontend: Ask repository question
    Frontend->>Backend: Send message with repository context
    Backend->>DB: Validate user, repository access, and conversation
    Backend->>Retrieval: Search authorized repository context
    Retrieval->>DB: Query chunks and embeddings
    DB-->>Retrieval: Relevant context with source metadata
    Retrieval-->>Backend: Ranked context
    Backend->>AI: Send prompt, question, and retrieved context
    AI-->>Backend: Draft answer
    Backend->>Backend: Validate citations and safety constraints
    Backend->>DB: Persist user message, assistant message, and sources
    Backend-->>Frontend: Return answer with citations
    Frontend-->>User: Display answer and cited files
```

AI chat requirements:

- Every chat request must be authorized against the repository.
- User messages should be validated for size and abuse controls.
- Conversations should preserve message history where useful, but retrieval should remain the source of repository truth.
- Assistant responses should include citations for repository claims.
- The UI should expose source files and line ranges when available.
- The backend should track token usage, model choice, latency, and error rates.
- The system should handle model errors, timeouts, and rate limits gracefully.

## 10. Background Job Architecture

Long-running and retryable work should run in background workers. The API should enqueue jobs and return status rather than blocking on expensive operations.

```mermaid
flowchart TB
    API["Backend API"] --> Queue["Job Queue"]
    Queue --> RepoWorker["Repository Worker"]
    Queue --> AIWorker["AI Worker"]
    Queue --> MaintenanceWorker["Maintenance Worker"]

    RepoWorker --> GitHub["GitHub Provider"]
    RepoWorker --> DB["PostgreSQL"]
    RepoWorker --> AIProvider["Embedding Provider"]

    AIWorker --> DB
    AIWorker --> AIProvider

    MaintenanceWorker --> DB
    MaintenanceWorker --> Storage["Object Storage"]

    RepoWorker --> Logs["Logs and Metrics"]
    AIWorker --> Logs
    MaintenanceWorker --> Logs
```

Job categories:

- Repository indexing jobs.
- Repository re-indexing jobs.
- Embedding generation jobs.
- Summary generation jobs.
- AI evaluation jobs.
- Cleanup and retention jobs.
- Webhook processing jobs.

Job architecture requirements:

- Jobs must be idempotent where possible.
- Job status must be persisted.
- Failed jobs must record safe diagnostic details.
- Retry policies must distinguish transient failures from permanent failures.
- Workers must enforce repository and tenant boundaries.
- Long-running jobs should emit progress events or status updates.
- Poison jobs should not block the queue indefinitely.

Recommended job states:

- `queued`
- `running`
- `succeeded`
- `failed`
- `cancelled`
- `retrying`

## 11. Deployment Architecture

Deployment should support separate development, staging, and production environments from the beginning.

```mermaid
flowchart TB
    Developer["Developer"] --> CI["CI Pipeline"]
    CI --> Tests["Lint, Type Check, Tests"]
    Tests --> Build["Build Images and Frontend Assets"]
    Build --> Registry["Container Registry"]

    Registry --> AppRuntime["Backend API Runtime"]
    Registry --> WorkerRuntime["Worker Runtime"]
    Build --> FrontendHost["Frontend Hosting"]

    FrontendHost --> CDN["CDN"]
    AppRuntime --> DB["Managed PostgreSQL"]
    AppRuntime --> Redis["Managed Redis"]
    WorkerRuntime --> DB
    WorkerRuntime --> Redis
    WorkerRuntime --> ObjectStorage["Object Storage"]

    AppRuntime --> Secrets["Secret Manager"]
    WorkerRuntime --> Secrets
    AppRuntime --> Observability["Observability Platform"]
    WorkerRuntime --> Observability
```

Deployment principles:

- Use separate environments for development, staging, and production.
- Run automated checks before deployment.
- Keep backend and worker deployments independently scalable.
- Validate configuration at startup.
- Store secrets in a managed secret store or deployment platform secret system.
- Run database migrations through controlled release steps.
- Define rollback procedures before production launch.
- Use health checks for API and worker processes.

Environment responsibilities:

- Development: Fast local feedback with Docker Compose or equivalent.
- Staging: Production-like validation, integration tests, and release verification.
- Production: Customer-facing environment with monitoring, backups, rate limits, and incident response.

## 12. Security Architecture

RepoMind AI handles source code, repository metadata, user identities, and provider credentials. Security must be a first-class architectural concern.

```mermaid
flowchart TB
    User["Authenticated User"] --> Session["Secure Session"]
    Session --> API["Backend API"]
    API --> AuthZ["Authorization Policies"]
    AuthZ --> TenantBoundary["Organization and Repository Boundary"]
    TenantBoundary --> Services["Application Services"]
    Services --> DataAccess["Data Access Layer"]
    DataAccess --> EncryptedDB["Encrypted Database Storage"]

    API --> RateLimit["Rate Limiting"]
    API --> Audit["Audit Logging"]
    Services --> SecretManager["Secret Manager"]
    Services --> Redaction["Log and Error Redaction"]
    Services --> ProviderTokens["Encrypted Provider Tokens"]
```

Security principles:

- Authenticate every protected request.
- Authorize every repository, conversation, job, and file access.
- Apply least privilege to provider tokens and service accounts.
- Encrypt secrets and provider tokens at rest.
- Use TLS for all network communication.
- Redact secrets, tokens, and private source content from logs.
- Maintain audit records for sensitive actions.
- Validate external inputs at API and application boundaries.
- Apply rate limits and abuse controls to AI and repository workflows.
- Isolate tenants by organization and repository access policy.

Security-sensitive data:

- OAuth access tokens and refresh tokens.
- Repository source code.
- Private repository metadata.
- User identity data.
- AI chat history containing repository context.
- Generated summaries and embeddings derived from private code.

Required controls:

- Token encryption at rest.
- Secure session cookies.
- CSRF protection for browser cookie flows.
- CORS allowlist configuration.
- Repository access checks before indexing and retrieval.
- Secret scanning safeguards during repository ingestion.
- Centralized authorization checks.
- Audit logs for repository connection, indexing, chat access, token revocation, and administrative actions.

## Cross-Cutting Architecture Concerns

### Observability

The system should provide enough visibility to debug failures, monitor costs, and understand product usage.

Required telemetry:

- API request latency and error rates.
- Background job duration, retries, and failures.
- Repository indexing throughput.
- AI provider latency, errors, and token usage.
- Retrieval quality signals.
- Authentication failures.
- Rate limit events.

### Configuration

Configuration must be environment-driven and validated at startup.

Configuration categories:

- Database connection settings.
- Redis connection settings.
- AI provider settings.
- GitHub OAuth and app settings.
- Session and cookie settings.
- Rate limits.
- Repository indexing limits.
- Logging level.
- Feature flags.

### Error Handling

Errors should be handled consistently across API and worker contexts.

Rules:

- Client-facing errors must be clear and safe.
- Internal logs should include correlation IDs and safe diagnostic metadata.
- Expected domain failures should map to typed application errors.
- Unexpected failures should be logged and surfaced as generic client errors.
- Worker failures should update persisted job status.

### Scalability

Early architecture should support future scale without premature complexity.

Scalability considerations:

- Queue-based repository indexing.
- Horizontal scaling for API and worker processes.
- Database indexes for user, repository, branch, indexing job, chat, citation, and audit lookup paths.
- Embedding model abstraction.
- Provider abstraction for repository services.
- Caching for repeated metadata and analysis status requests.
- Incremental re-indexing based on content hashes and provider events.

## Implementation Readiness Checklist

Before application code is generated, confirm:

- Product scope for the MVP is aligned with `docs/PRODUCT_VISION.md` and `docs/PROJECT_ROADMAP.md`.
- The canonical database table names match `docs/DATABASE.md`: `users`, `user_profiles`, `repositories`, `repository_branches`, `repository_files`, `code_chunks`, `embeddings`, `indexing_jobs`, `chat_sessions`, `chat_messages`, `citations`, `dependency_edges`, `architecture_snapshots`, `api_keys`, and `audit_logs`.
- API endpoints in `docs/API_SPEC.md` map to the database tables they read and write.
- UI pages in `docs/UI_UX.md` are backed by current API capabilities or clearly marked as future functionality.
- Security controls in `docs/SECURITY.md` cover the same API resources and database tables.
- Deployment assumptions in `docs/DEPLOYMENT.md` support separate frontend, backend API, worker, PostgreSQL, Redis, and AI provider configuration.
- Testing expectations in `docs/TESTING_STRATEGY.md` cover backend, frontend, API, security, performance, and AI/RAG behavior.
- No implementation starts until environment variables, secret handling, migration strategy, and repository indexing limits are defined for the first development milestone.

## Architecture Decision Records

Significant future decisions should be captured as architecture decision records.

Examples:

- Frontend framework selection.
- Background job library selection.
- Initial vector search strategy.
- Authentication provider and session strategy.
- GitHub OAuth versus GitHub App integration.
- AI provider and model selection.
- Deployment platform selection.

Each decision record should document context, decision, alternatives considered, tradeoffs, and consequences.
