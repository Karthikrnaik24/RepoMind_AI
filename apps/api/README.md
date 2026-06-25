# RepoMind AI API

Backend API application for RepoMind AI.

## Purpose

This app contains the FastAPI service and future worker entry points for repository intelligence workflows.

## Structure

- `app/`: Python application package.
- `app/domain/`: Domain entities, value objects, policies, and ports.
- `app/application/`: Use cases and orchestration services.
- `app/application/services/`: Service layer with constructor-injected repositories.
- `app/repositories/`: SQLAlchemy repository layer; future services should not expose ORM queries.
- `app/core/`: Cross-cutting exceptions and structured logging.
- `app/infrastructure/`: Database, queue, provider, and external service adapters.
- `app/interfaces/`: HTTP routes and future inbound adapters.
- `app/interfaces/api/v1/`: Versioned REST API routes.
- `app/interfaces/api/schemas/`: Request and response DTOs.
- `app/middleware/`: Request ID, logging, and error middleware.
- `app/config/`: Environment-driven settings.
- `tests/`: Backend test suite.
- `alembic/`: Database migration environment.

Only system health and status endpoints are implemented at this stage. Versioned API responses use the standard `{ "success": true, "data": {}, "meta": {} }` envelope.

## Supabase Identity Foundation

Sprint 3.1 loads Supabase configuration and prepares JWT verification utilities. It does not require authentication on any route.

Required backend variables:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_JWT_SECRET`

`GET /api/v1/status` reports whether Supabase configuration exists without calling Supabase APIs.
