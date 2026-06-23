# Contributing to RepoMind AI

Thank you for contributing to RepoMind AI. This project is being built as a long-term production product, so contributions should prioritize correctness, maintainability, security, and clear communication.

Before writing code, read the relevant project documentation in `docs/`, especially:

- `docs/PRODUCT_VISION.md`
- `docs/ARCHITECTURE.md`
- `docs/TECH_STACK.md`
- `docs/CODING_STANDARDS.md`
- `docs/SECURITY.md`
- `docs/API_SPEC.md`

## Project Setup

The application implementation has not been generated yet. Until the frontend, backend, and infrastructure folders exist, setup is limited to cloning the repository and reviewing the documentation baseline.

Expected future setup flow:

1. Clone the repository.
2. Install frontend dependencies from the `frontend/` directory.
3. Install backend dependencies from the `backend/` directory.
4. Copy environment examples into local-only environment files.
5. Start local infrastructure with Docker Compose.
6. Run database migrations.
7. Start the backend API, background worker, and frontend app.

Setup rules:

- Never commit real secrets or local `.env` files.
- Keep development, staging, and production configuration separate.
- Update setup documentation whenever setup steps change.

## Folder Structure

Recommended top-level structure:

```text
/
  docs/
  frontend/
  backend/
  infra/
  scripts/
  .github/
  README.md
  CONTRIBUTING.md
```

Expected backend structure:

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

Expected frontend structure:

```text
frontend/
  src/
    app/
    api/
    components/
    features/
    hooks/
    lib/
    styles/
    types/
    tests/
```

See `docs/CODING_STANDARDS.md` for detailed folder responsibilities and dependency rules.

## Coding Standards

All contributions must follow the standards in `docs/CODING_STANDARDS.md`.

Core expectations:

- Prefer clear, readable code over clever shortcuts.
- Keep business logic separate from frameworks.
- Use TypeScript best practices in the frontend.
- Use Python best practices in the backend.
- Validate all external input.
- Handle errors explicitly.
- Add structured logging where operationally useful.
- Never hardcode secrets or environment-specific values.
- Keep changes focused and appropriately scoped.
- Update documentation alongside behavior, architecture, setup, or workflow changes.

Architecture expectations:

- Follow Clean Architecture boundaries.
- Keep domain logic independent from FastAPI, SQLAlchemy, AI SDKs, and provider SDKs.
- Keep frontend API access centralized.
- Keep AI provider usage behind internal interfaces.
- Keep repository provider integrations behind internal interfaces.

## Branch Strategy

Use short-lived branches and merge through pull requests.

Default branch:

- `main` should remain deployable.

Branch naming format:

```text
<type>/<short-description>
```

Recommended branch types:

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
docs/contributing-guide
feature/repository-indexing
fix/oauth-callback-validation
security/token-redaction
```

For Codex-generated branches in this workspace, use the configured `codex/` prefix unless a different branch name is explicitly requested.

## Pull Request Rules

Pull requests should be small, focused, and reviewable.

Every pull request should include:

- Clear summary of the change.
- Reason for the change.
- Testing performed.
- Documentation updated, or a reason documentation is not needed.
- Security considerations when the change touches auth, repositories, AI, secrets, files, or database access.
- Screenshots or recordings for user-facing UI changes.

Pull request requirements:

- CI must pass before merge once CI is configured.
- Database migrations must be reviewed carefully.
- Security-sensitive changes require extra scrutiny.
- Avoid mixing unrelated refactors with feature work.
- Avoid large pull requests unless the scope genuinely requires them.
- Do not merge code that knowingly breaks setup, tests, or documented workflows.

## Commit Message Conventions

Use Conventional Commits.

Format:

```text
<type>(optional-scope): <summary>
```

Allowed types:

- `feat`: New product or system capability.
- `fix`: Bug fix.
- `docs`: Documentation-only change.
- `refactor`: Internal restructuring without behavior change.
- `test`: Test additions or updates.
- `chore`: Maintenance task.
- `build`: Build or dependency changes.
- `ci`: CI/CD changes.
- `perf`: Performance improvement.
- `security`: Security-related change.

Examples:

```text
docs: add contributing guide
feat(indexing): add repository file scanner
fix(auth): validate oauth state
security(api): redact authorization headers from logs
```

Commit rules:

- Keep commits focused.
- Use imperative, concise summaries where practical.
- Add a commit body when context or tradeoffs are not obvious.
- Never include secrets, tokens, private source content, or customer data in commit messages.

## Review Checklist

Reviewers should verify:

- The change solves the stated problem.
- The implementation matches the documented architecture.
- Code is readable, typed, and maintainable.
- Input validation is present at external boundaries.
- Errors are handled safely and consistently.
- Logs are useful and do not expose sensitive data.
- Secrets and configuration are not hardcoded.
- Authorization checks are present for protected resources.
- Tests cover important behavior and edge cases.
- Documentation is updated when needed.
- Performance, scalability, and security impacts are understood.

For AI-related changes, also verify:

- Repository-specific claims are grounded in retrieved context.
- Citations are preserved where required.
- Prompt changes are reviewable.
- Token usage and cost impact are considered.
- Failure behavior is defined for insufficient context or provider errors.

## Testing Requirements

Testing should scale with risk.

Expected test categories:

- Unit tests for domain and application logic.
- Component tests for reusable frontend behavior.
- Integration tests for API, database, repository ingestion, queues, and provider adapters.
- End-to-end tests for critical user workflows.
- Regression tests for retrieval and AI response quality as the product matures.

Minimum expectations:

- New behavior should include tests unless the change is documentation-only.
- Bug fixes should include a regression test when practical.
- Security-sensitive changes should include negative tests for unauthorized or invalid input.
- Database changes should be tested against migrated schema.
- UI changes should be verified for loading, empty, and error states.

If tests cannot be added, explain why in the pull request and describe manual verification.

## Documentation Rules

Documentation is part of the product.

Update documentation when changing:

- Product behavior.
- API contracts.
- Database schema.
- Architecture boundaries.
- Security controls.
- Deployment or setup steps.
- UI/UX workflows.
- Coding standards.

Documentation expectations:

- Keep documents accurate and concise.
- Link to the most relevant existing docs instead of duplicating large sections.
- Document tradeoffs for significant decisions.
- Add architecture decision records for major technology or architecture choices.
- Keep examples safe and free of real secrets.

Documentation-only changes do not require application tests, but they should still be reviewed for clarity, consistency, and long-term usefulness.
