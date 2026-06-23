# RepoMind AI Technical Stack

## Stack Philosophy

RepoMind AI should be built on stable, widely adopted technologies that support maintainability, scalability, security, and hiring over the long term.

Technology choices should favor:

- Strong typing and clear interfaces.
- Excellent ecosystem support.
- Production reliability.
- Testability.
- Observability.
- Clean separation between domain logic, infrastructure, and user interface.
- The ability to replace vendors or infrastructure components without rewriting core business logic.

This document describes the recommended initial stack. Final choices can evolve through architecture decision records as the product matures.

## Frontend

Recommended technologies:

- TypeScript
- React
- Vite or Next.js
- Tailwind CSS or a component system built on accessible primitives
- TanStack Query
- React Hook Form with Zod validation
- Playwright for end-to-end testing
- Vitest and React Testing Library for unit and component testing

Justification:

- TypeScript improves maintainability and catches integration errors early.
- React has strong ecosystem support and hiring availability.
- Vite is lightweight and fast for application development. Next.js is appropriate if server-side rendering, routing conventions, or full-stack deployment benefits become important.
- Accessible UI primitives reduce the risk of inconsistent or inaccessible interfaces.
- TanStack Query provides reliable server-state management for repository analysis jobs, polling, caching, and mutations.
- React Hook Form and Zod provide a clean path for validating user input at the UI boundary.
- Playwright supports production-grade browser workflow verification.

Frontend architecture guidance:

- Keep UI components separate from API clients and domain-specific state.
- Validate all user-controlled input before submitting it to the backend.
- Treat backend API contracts as typed interfaces.
- Avoid storing secrets in frontend code.

## Backend

Recommended technologies:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- Celery, RQ, or Dramatiq for background jobs
- Pytest for testing
- Ruff for linting and formatting
- Mypy or Pyright for static typing where practical

Justification:

- Python is well suited for AI orchestration, repository analysis, text processing, and integration with model providers.
- FastAPI provides strong support for typed API contracts, validation, dependency injection, and OpenAPI documentation.
- Pydantic gives robust request and configuration validation.
- SQLAlchemy and Alembic are mature choices for relational persistence and migrations.
- Background jobs are necessary because repository analysis, embeddings, and AI workflows may exceed request-response time limits.
- Pytest has a strong ecosystem for unit, integration, and service-level testing.
- Ruff provides fast, consistent linting and formatting.

Backend architecture guidance:

- Use Clean Architecture boundaries: domain, application, infrastructure, and interface layers.
- Keep framework-specific code at the edges.
- Keep AI provider calls behind interfaces.
- Keep repository provider integrations behind interfaces.
- Validate inputs at API boundaries and again at critical application service boundaries.
- Use structured logging and avoid logging secrets, access tokens, or full private repository content.

## Database

Recommended technologies:

- PostgreSQL
- pgvector for vector search during early product stages
- Redis for caching, rate limiting, and job coordination where needed

Justification:

- PostgreSQL is reliable, widely supported, and well suited for structured product data.
- pgvector allows the MVP to keep relational data and vector search in one operational system, reducing infrastructure complexity.
- Redis is useful for queues, short-lived cache, locks, and rate limiting.

Expected data domains:

- Users and organizations.
- Repositories.
- Repository analysis jobs.
- File metadata.
- Content chunks.
- Embeddings.
- AI conversations and messages.
- Source references.
- Audit events.

Future considerations:

- A dedicated vector database may be introduced if scale, latency, metadata filtering, or hybrid search requirements exceed pgvector capabilities.
- Object storage may be needed for large generated artifacts, repository snapshots, or exported documentation.

## AI

Recommended technologies and patterns:

- OpenAI or compatible LLM provider through a provider abstraction.
- Embedding model for repository retrieval.
- Retrieval-augmented generation for grounded answers.
- Prompt templates versioned in the codebase.
- Source citation enforcement.
- Evaluation datasets for answer quality.

Justification:

- AI providers and models change quickly, so application code should depend on internal interfaces rather than direct provider usage throughout the codebase.
- Retrieval-augmented generation is necessary to ground responses in repository content.
- Versioned prompts make behavior easier to review and improve.
- Evaluation datasets help prevent regressions as prompts, chunking, retrieval, and models evolve.

AI safety and quality rules:

- Answers must cite repository sources when making repository-specific claims.
- Responses should distinguish facts from inferences.
- The system should decline or ask for clarification when context is insufficient.
- Secrets and private repository content must be protected in logs, telemetry, and third-party integrations.
- Model configuration must be environment-driven, never hardcoded.

## Infrastructure

Recommended technologies:

- Docker for local and production packaging.
- Docker Compose for local development.
- PostgreSQL managed service in production.
- Redis managed service in production.
- Object storage such as S3-compatible storage for artifacts.
- OpenTelemetry-compatible observability.

Justification:

- Docker improves consistency across development, testing, and deployment.
- Managed database and Redis services reduce operational burden during early growth.
- Object storage provides a scalable path for large files and exports.
- OpenTelemetry avoids locking observability data into one vendor too early.

Infrastructure requirements:

- Environment-based configuration.
- Secret management through the deployment platform or a secret manager.
- Health checks for services.
- Structured logs.
- Metrics for API latency, job duration, token usage, retrieval quality, and failure rates.
- Backups for persistent data.

## Deployment

Recommended initial deployment options:

- Frontend: Vercel, Netlify, or containerized deployment.
- Backend: Render, Fly.io, Railway, AWS ECS, Google Cloud Run, or Kubernetes when justified.
- Database: Managed PostgreSQL.
- Queue workers: Containerized worker processes.

Justification:

- Early deployment should minimize operational complexity while preserving a migration path to more controlled infrastructure.
- Containerized backend and workers avoid platform lock-in.
- Managed services let the team focus on product and reliability before building an operations-heavy platform.

Deployment expectations:

- Separate development, staging, and production environments.
- CI checks before merge.
- Database migrations run through controlled release steps.
- Rollback strategy documented before production usage.
- No secrets committed to the repository.

## Development Tools

Recommended tools:

- Git and GitHub or GitLab.
- GitHub Actions or GitLab CI.
- Pre-commit hooks.
- ESLint and Prettier for frontend consistency.
- Ruff and Pytest for backend consistency.
- Mypy or Pyright for backend type checks where appropriate.
- Playwright for end-to-end tests.
- Dependabot or Renovate for dependency updates.
- Architecture decision records for significant technical decisions.

Justification:

- Automated checks reduce review burden and prevent avoidable regressions.
- Consistent formatting keeps diffs focused on behavior.
- Dependency automation helps manage security updates.
- Architecture decision records preserve the reasoning behind important choices.

## Configuration and Secrets

Configuration rules:

- Use environment variables for runtime configuration.
- Validate configuration at service startup.
- Keep local examples in `.env.example`.
- Never commit real secrets.
- Rotate credentials if accidental exposure occurs.

Examples of configuration categories:

- Database connection settings.
- Redis connection settings.
- AI provider keys and model names.
- Repository provider credentials.
- Logging level.
- Rate limits.
- Feature flags.

## Testing Strategy

Required test categories:

- Unit tests for domain and application logic.
- Integration tests for database, repository ingestion, retrieval, and API behavior.
- Contract tests for API schemas where practical.
- End-to-end tests for critical user workflows.
- Regression tests for AI prompts and retrieval behavior.

Testing priorities:

- Input validation.
- Repository ingestion edge cases.
- File filtering and size limits.
- Retrieval correctness.
- AI answer grounding.
- Authorization and tenant isolation once team features exist.

## Technology Decision Process

Every major technology decision should include:

- Problem being solved.
- Options considered.
- Decision.
- Tradeoffs.
- Security and operational impact.
- Migration considerations.

These decisions should be recorded as architecture decision records when they materially affect product direction, scalability, or maintainability.
