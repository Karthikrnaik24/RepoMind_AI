# ADR 0001: Use Clean Architecture

## Status

Accepted

## Context

RepoMind AI is intended to become a production-grade repository intelligence platform with multiple workflows: authentication, repository ingestion, indexing, search, RAG, chat, billing, and administration.

Without clear boundaries, API routes can easily become tightly coupled to persistence details, external provider SDKs, and AI orchestration code. That coupling would slow future feature delivery and make testing expensive.

## Decision

RepoMind AI will use Clean Architecture principles for the backend:

- HTTP routes live in `interfaces`.
- Application orchestration lives in `application/services`.
- Persistence access lives behind repositories in `repositories`.
- Database and provider adapters live in `infrastructure`.
- Cross-cutting concerns live in `core`.
- Domain logic will live in `domain` as it is introduced.

Dependencies should point inward. Future services should depend on repository abstractions or explicit ports instead of direct ORM queries.

## Consequences

Positive outcomes:

- Business workflows can be tested without running FastAPI.
- Persistence implementation details stay isolated.
- Future integrations can be introduced behind adapters.
- DTOs prevent ORM models from leaking through API responses.

Tradeoffs:

- More files and constructors are required early.
- Developers must respect dependency boundaries during feature work.
- Small changes may require touching multiple layers.
