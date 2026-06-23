# RepoMind AI API

Backend API application for RepoMind AI.

## Purpose

This app contains the FastAPI service and future worker entry points for repository intelligence workflows.

## Structure

- `app/`: Python application package.
- `app/domain/`: Domain entities, value objects, policies, and ports.
- `app/application/`: Use cases and orchestration services.
- `app/infrastructure/`: Database, queue, provider, and external service adapters.
- `app/interfaces/`: HTTP routes and future inbound adapters.
- `app/config/`: Environment-driven settings.
- `tests/`: Backend test suite.
- `alembic/`: Database migration environment.

Only the health endpoint is implemented at this stage.
