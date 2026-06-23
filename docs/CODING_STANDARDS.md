# RepoMind AI Coding Standards

## Purpose

These standards define how RepoMind AI should be built as a maintainable, production-grade software product.

The goal is not to create process for its own sake. The goal is to make the codebase easier to understand, safer to change, and ready to support a growing team and user base.

## Engineering Principles

Core principles:

- Prefer clarity over cleverness.
- Keep business logic independent from frameworks.
- Use strong typing at service boundaries.
- Validate all external input.
- Handle errors explicitly.
- Log operationally useful events without exposing secrets.
- Keep modules focused and cohesive.
- Avoid hidden coupling.
- Write tests for behavior that matters.
- Document decisions that future engineers will need to understand.

## Folder Organization

The exact structure may evolve, but the project should use clear boundaries from the beginning.

Recommended top-level organization:

```text
/
  docs/
  frontend/
  backend/
  infra/
  scripts/
  .github/
  README.md
```

### Backend Organization

Recommended backend structure:

```text
backend/
  app/
    domain/
    application/
    infrastructure/
    interfaces/
    config/
    shared/
  tests/
    unit/
    integration/
    e2e/
  migrations/
```

Layer responsibilities:

- `domain`: Core entities, value objects, domain rules, and interfaces that should not depend on frameworks.
- `application`: Use cases, orchestration, commands, queries, and service coordination.
- `infrastructure`: Database, external APIs, AI providers, repository providers, queues, and file system adapters.
- `interfaces`: HTTP routes, request and response schemas, CLI adapters, and other inbound delivery mechanisms.
- `config`: Environment-driven configuration and startup validation.
- `shared`: Small cross-cutting utilities used carefully and sparingly.

Rules:

- Domain code must not import FastAPI, SQLAlchemy, AI SDKs, or infrastructure adapters.
- Application services may depend on domain interfaces, not concrete infrastructure classes.
- Infrastructure implements interfaces defined by domain or application layers.
- HTTP routes should be thin and delegate work to application services.

### Frontend Organization

Recommended frontend structure:

```text
frontend/
  src/
    app/
    components/
    features/
    api/
    hooks/
    lib/
    styles/
    types/
    tests/
```

Responsibilities:

- `app`: Application shell, routing, providers, and page-level composition.
- `components`: Reusable UI components that are not tied to one feature.
- `features`: Domain-specific UI, state, and workflows.
- `api`: API clients, request/response types, and server-state hooks.
- `hooks`: Shared React hooks.
- `lib`: Generic helpers with no UI dependency.
- `styles`: Global styles and design tokens.
- `types`: Shared frontend type definitions.

Rules:

- Keep business workflows in feature modules, not scattered across page components.
- Keep API calls centralized.
- Keep components accessible and keyboard-friendly.
- Do not hardcode secrets or environment-specific URLs.

## Naming Conventions

### General

- Use descriptive names that reveal intent.
- Avoid abbreviations unless they are widely understood.
- Avoid names such as `data`, `item`, `obj`, or `temp` when a domain-specific name is available.
- Name booleans as predicates, such as `isAnalyzed`, `hasErrors`, or `canRetry`.

### TypeScript

- Files: `kebab-case.ts` or `kebab-case.tsx`.
- React components: `PascalCase`.
- Hooks: `useCamelCase`.
- Functions and variables: `camelCase`.
- Types and interfaces: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE` for true constants, `camelCase` for local immutable values.

### Python

- Files and modules: `snake_case.py`.
- Classes: `PascalCase`.
- Functions and variables: `snake_case`.
- Constants: `UPPER_SNAKE_CASE`.
- Private helpers: prefix with a single underscore when module-private intent is meaningful.

### Database

- Tables: `snake_case`, plural nouns where practical.
- Columns: `snake_case`.
- Primary keys: `id`.
- Foreign keys: `<entity>_id`.
- Timestamp columns: `created_at`, `updated_at`, and domain-specific timestamps as needed.

## Git Strategy

Default strategy:

- Use trunk-based development with short-lived feature branches.
- Keep `main` deployable.
- Merge through pull requests.
- Require automated checks before merge.
- Prefer small, focused pull requests.

Protected branch expectations:

- `main` should require passing CI.
- `main` should require review before merge once more than one contributor is active.
- Direct commits to `main` should be avoided except for exceptional maintenance cases.

## Branch Naming

Use lowercase branch names with hyphen-separated words.

Recommended format:

```text
<type>/<short-description>
```

Allowed types:

- `feature`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`
- `infra`
- `security`

Examples:

```text
feature/repository-ingestion
fix/analysis-job-retry
docs/product-roadmap
infra/docker-compose
security/token-redaction
```

For Codex-generated branches in this workspace, use the configured `codex/` prefix when creating branches unless a different branch naming convention is explicitly requested.

## Commit Message Format

Use concise, descriptive commit messages based on Conventional Commits.

Format:

```text
<type>(optional-scope): <summary>
```

Allowed types:

- `feat`: New user-facing or system capability.
- `fix`: Bug fix.
- `docs`: Documentation-only change.
- `refactor`: Internal restructuring without behavior change.
- `test`: Test additions or updates.
- `chore`: Maintenance task.
- `build`: Build system or dependency changes.
- `ci`: Continuous integration changes.
- `perf`: Performance improvement.
- `security`: Security-related change.

Examples:

```text
docs: add foundational project documentation
feat(ingestion): add repository file scanner
fix(api): validate repository URL input
refactor(ai): isolate provider client interface
```

Commit rules:

- Keep commits focused.
- Write summaries in the imperative mood where practical.
- Include context in the body when the reason is not obvious.
- Do not include secrets, tokens, or sensitive repository data in commit messages.

## Code Review Checklist

Reviewers should check for:

- The change solves the stated problem.
- The implementation follows Clean Architecture boundaries.
- Names are clear and domain-appropriate.
- Input validation is present at external boundaries.
- Errors are handled explicitly and consistently.
- Logs are useful and do not expose secrets or sensitive repository content.
- Configuration is environment-driven.
- Tests cover important behavior and edge cases.
- Public APIs and contracts are documented.
- Database migrations are safe and reversible where practical.
- Performance implications are understood.
- Security and authorization implications are considered.
- The change is appropriately scoped.
- Documentation is updated when behavior, architecture, setup, or workflows change.

For AI-related changes, reviewers should also check:

- Prompts are versioned or easy to review.
- Outputs are grounded in retrieved context where repository-specific claims are made.
- Source references are preserved.
- Failure and insufficient-context behavior is defined.
- Token usage and cost implications are considered.

## Documentation Rules

Documentation should live close to the work it explains.

Required documentation:

- Product and roadmap documentation in `docs/`.
- Technical stack and coding standards in `docs/`.
- Setup instructions in `README.md`.
- Architecture decision records for major technical decisions.
- API documentation generated from backend schemas when available.
- Inline comments only when code intent is not obvious.

Documentation standards:

- Keep documentation accurate and updated with related changes.
- Prefer concise explanations with clear ownership and context.
- Document tradeoffs for significant decisions.
- Avoid duplicating implementation details that will become stale quickly.
- Include examples for configuration, commands, and workflows when useful.

## Error Handling

Error handling rules:

- Validate all external input before use.
- Return clear, safe error messages to users.
- Preserve detailed diagnostic context in logs where safe.
- Do not expose stack traces, secrets, tokens, or private repository content in client-facing errors.
- Use typed or structured errors in application code.
- Handle expected failure modes explicitly.

Expected failure modes:

- Invalid repository URL or unsupported provider.
- Repository access denied.
- Repository too large.
- Unsupported file types.
- AI provider timeout or rate limit.
- Embedding generation failure.
- Database or queue unavailable.

## Logging Standards

Logging rules:

- Use structured logs.
- Include correlation or request IDs when available.
- Log important lifecycle events such as repository analysis started, completed, failed, or retried.
- Redact secrets and credentials.
- Avoid logging full private source files.
- Use appropriate log levels.

Recommended levels:

- `debug`: Diagnostic details for local development or targeted investigation.
- `info`: Important lifecycle events.
- `warning`: Recoverable unexpected conditions.
- `error`: Failed operations requiring attention.
- `critical`: System-wide failures or data integrity risks.

## Testing Standards

Testing expectations:

- Unit tests for domain and application logic.
- Integration tests for database, API, queues, repository ingestion, and AI provider adapters.
- End-to-end tests for critical user workflows.
- Regression tests for retrieval and AI answer quality as the product matures.

Test naming:

- Test names should describe behavior.
- Avoid testing implementation details unless necessary.
- Prefer realistic fixtures for repository ingestion and retrieval behavior.

Coverage priorities:

- Input validation.
- Repository parsing edge cases.
- Permission and access control behavior.
- Background job retries and failure states.
- AI grounding and citation behavior.

## Security Standards

Security rules:

- Never hardcode secrets.
- Never commit `.env` files containing real credentials.
- Store secrets in environment variables or a managed secret store.
- Validate and sanitize all user input.
- Apply least privilege for repository provider tokens.
- Redact credentials from logs and error messages.
- Design for tenant isolation before multi-tenant features are launched.
- Review dependencies regularly for vulnerabilities.

## Configuration Standards

Configuration rules:

- All environment-specific values must come from environment variables or a configuration provider.
- Configuration must be validated at startup.
- Provide safe local defaults only when they do not hide production requirements.
- Maintain `.env.example` when application configuration is introduced.
- Keep model names, provider URLs, limits, and feature flags configurable.

## Definition of Done

A change is considered done when:

- It satisfies the requested behavior.
- It follows the architecture and coding standards.
- It includes appropriate tests or a clear reason tests are not applicable.
- It includes validation, error handling, and logging where relevant.
- Documentation is updated.
- CI checks pass locally or in the remote pipeline.
- Security and configuration concerns have been reviewed.

For documentation-only changes, the definition of done is:

- The documents are clear, consistent, and complete for the requested scope.
- They do not introduce application code.
- They align with the long-term product direction.
