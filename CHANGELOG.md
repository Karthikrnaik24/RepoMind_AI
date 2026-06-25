# Changelog

All notable changes to RepoMind AI will be documented in this file.

## v0.1.0

Initial foundation release for RepoMind AI.

### Added

- Monorepo foundation with `apps`, `packages`, `infra`, `docker`, `scripts`, and `docs` structure.
- FastAPI backend foundation with Clean Architecture layering, health/status endpoints, SQLAlchemy, Alembic, Ruff, Pytest, dependency injection, middleware, structured logging, exception handling, and repository/service layers.
- Next.js frontend foundation using the App Router, TypeScript, Tailwind CSS, shadcn/ui setup, ESLint, Prettier, Husky, and lint-staged.
- PostgreSQL and pgvector database design with production-oriented schema documentation, ORM model foundations, and Alembic migration structure.
- Supabase identity foundation with frontend Supabase SDK factories, backend Supabase configuration, JWT verifier utilities, identity abstractions, and identity service scaffolding.
- Docker development setup with frontend, backend, PostgreSQL, and Redis services.
- GitHub Actions CI for frontend lint/typecheck/tests and backend lint/tests.
- Product, architecture, database, API, UI/UX, security, deployment, testing, backend architecture, auth architecture, and ADR documentation.
