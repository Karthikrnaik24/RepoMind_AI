# ADR 0002: Use FastAPI

## Status

Accepted

## Context

RepoMind AI needs a Python backend that can expose REST APIs, validate request and response DTOs, integrate with async infrastructure over time, and support a strong testing workflow.

The backend will eventually coordinate database access, background jobs, GitHub provider calls, repository indexing, and AI/RAG workflows.

## Decision

RepoMind AI will use FastAPI for the backend API.

Reasons:

- First-class Pydantic integration for typed request and response schemas.
- Strong OpenAPI generation for frontend and integration consumers.
- Dependency injection support for settings, sessions, repositories, and services.
- Good compatibility with Python async workflows.
- Mature ecosystem for middleware, testing, and deployment.

## Consequences

Positive outcomes:

- API contracts can be documented and validated automatically.
- DTOs and response models remain explicit.
- Dependency injection supports Clean Architecture boundaries.
- Tests can exercise routes without a running HTTP server.

Tradeoffs:

- FastAPI-specific dependencies must stay in the interface layer.
- Application services should not import FastAPI objects.
- Middleware and exception handling need careful conventions to keep API responses consistent.
