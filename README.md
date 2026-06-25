# RepoMind AI

RepoMind AI is a production-oriented repository intelligence platform for understanding, indexing, searching, and discussing software repositories with AI-assisted workflows.

This repository is currently in the foundation phase. The structure below defines ownership boundaries before application logic is introduced.

## Monorepo Structure

```text
RepoMind_AI/
  apps/
    web/
    api/
  packages/
    shared/
    ai/
    parser/
    github/
    embeddings/
    rag/
  infra/
  docker/
  scripts/
  docs/
  .github/
```

## Directory Purposes

- `apps/`: Deployable applications.
- `apps/web/`: Frontend web application. This will eventually contain the TypeScript user interface.
- `apps/api/`: Backend API application. This will eventually contain the Python API service and worker entry points.
- `packages/`: Reusable internal packages shared across apps.
- `packages/shared/`: Shared contracts, constants, validation schemas, and cross-cutting utilities.
- `packages/ai/`: AI provider abstractions, model orchestration helpers, and prompt-facing interfaces.
- `packages/parser/`: Repository parsing, language detection, file classification, and code chunking utilities.
- `packages/github/`: GitHub provider integration boundaries and future GitHub API adapters.
- `packages/embeddings/`: Embedding provider abstractions and embedding pipeline utilities.
- `packages/rag/`: Retrieval-augmented generation interfaces, retrieval policies, and citation assembly utilities.
- `infra/`: Infrastructure-as-code and deployment environment definitions.
- `docker/`: Dockerfiles, Compose files, and container runtime assets.
- `scripts/`: Development, maintenance, migration, and operational scripts.
- `docs/`: Product, architecture, database, API, security, deployment, testing, and UX documentation.
- `.github/`: GitHub-specific automation such as workflows, issue templates, pull request templates, and repository governance.

## Current Scope

No application logic has been implemented yet. See `docs/` for the product and engineering foundation before creating application code.

Backend architecture hardening is documented in `docs/BACKEND_ARCHITECTURE.md`, including the repository pattern, service layer, DTOs, middleware, logging, and versioned API conventions.

## Local Development

### Frontend

```powershell
cd apps/web
npm ci
npm run dev
```

The frontend runs at `http://localhost:3000` by default. Copy `apps/web/.env.example` to `apps/web/.env.local` when local environment configuration is needed.

### Backend

```powershell
cd apps/api
uv sync --all-groups
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend health endpoint runs at `http://localhost:8000/health`. Copy `apps/api/.env.example` to `apps/api/.env` for local configuration.

### Docker Compose

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Docker Compose starts the frontend, backend, PostgreSQL with pgvector, and Redis. Use local-only credentials for development and never commit real secrets.

## Supabase Setup

Sprint 3.1 configures Supabase identity infrastructure only. It does not add login, OAuth callbacks, RBAC, or protected routes.

Required frontend variables:

```text
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

Required backend variables:

```text
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
```

Copy `.env.example` to `.env` for Docker Compose, `apps/web/.env.example` to `apps/web/.env.local` for frontend-only development, and `apps/api/.env.example` to `apps/api/.env` for backend-only development.

Never expose `SUPABASE_SERVICE_ROLE_KEY` or `SUPABASE_JWT_SECRET` in the frontend.

See `docs/AUTH_ARCHITECTURE.md` for the identity, JWT, OAuth, user synchronization, and future RBAC design.
