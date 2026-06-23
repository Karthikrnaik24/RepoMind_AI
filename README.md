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
