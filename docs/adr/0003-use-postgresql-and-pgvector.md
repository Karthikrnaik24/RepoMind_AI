# ADR 0003: Use PostgreSQL and pgvector

## Status

Accepted

## Context

RepoMind AI needs a durable system of record for users, repositories, branches, files, chunks, embeddings, indexing jobs, chat sessions, citations, dependency edges, architecture snapshots, API keys, and audit logs.

The product also needs vector retrieval for repository understanding and future RAG workflows.

## Decision

RepoMind AI will use PostgreSQL as the primary database and pgvector for early vector search.

Reasons:

- PostgreSQL provides strong relational integrity for core product data.
- Alembic and SQLAlchemy support a controlled migration workflow.
- pgvector keeps early semantic retrieval close to relational metadata.
- PostgreSQL supports JSONB, indexing, constraints, transactions, and future partitioning.
- The design leaves a path to a dedicated vector database if scale requires it.

## Consequences

Positive outcomes:

- Repository intelligence data remains auditable and relationally consistent.
- Embeddings can be joined with files, chunks, jobs, repositories, and citations.
- Early production infrastructure remains simpler than operating a separate vector store.

Tradeoffs:

- PostgreSQL-specific features require PostgreSQL-backed integration tests.
- SQLite should only be used for lightweight unit tests that do not exercise PostgreSQL types or migrations.
- Vector performance must be monitored as repository volume grows.
