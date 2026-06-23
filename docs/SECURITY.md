# RepoMind AI Security Architecture

## Purpose

This document defines the security architecture for RepoMind AI. It is documentation only and does not introduce implementation code, routes, middleware, configuration files, or infrastructure definitions.

RepoMind AI will process sensitive assets: private repository source code, repository metadata, user identities, OAuth tokens, AI prompts, generated summaries, embeddings, chat history, API keys, and audit logs. Security must be designed into the product from the beginning rather than added after launch.

## Security Principles

- Apply least privilege everywhere.
- Authenticate every protected request.
- Authorize every repository-scoped action.
- Treat repository content and derived AI artifacts as sensitive data.
- Never hardcode secrets or commit credentials.
- Validate all external input.
- Use secure defaults and explicit allowlists.
- Log enough for security investigation without exposing secrets.
- Encrypt sensitive data in transit and at rest.
- Keep security controls testable and reviewable.
- Prefer defense in depth over single points of trust.

## API and Database Security Alignment

Security rules must align with the REST API in `docs/API_SPEC.md` and the canonical tables in `docs/DATABASE.md`.

Protected resource mapping:

| Resource area | API capabilities | Database tables requiring authorization |
| --- | --- | --- |
| User identity | Login, logout, refresh token, profile | `users`, `user_profiles` |
| Repositories | Connect GitHub, list repositories, repository details | `repositories`, `repository_branches` |
| Indexing | Start indexing, index status | `indexing_jobs`, `repository_files`, `code_chunks`, `embeddings` |
| Files | List files, read file, explain file | `repository_files`, `code_chunks`, `embeddings`, `citations` |
| Search | Semantic search, keyword search | `repository_files`, `code_chunks`, `embeddings` |
| Chat | Create session, send message, conversation history | `chat_sessions`, `chat_messages`, `citations` |
| Dependency graph | Dependency graph | `dependency_edges`, `repository_files` |
| Architecture | Architecture diagram, repository summary | `architecture_snapshots`, `repository_files`, `code_chunks`, `citations` |
| Programmatic access | Future API key management | `api_keys`, `audit_logs` |
| Auditability | Security and operational event capture | `audit_logs` |

Alignment requirements:

- Repository-scoped API endpoints must authorize against `repositories` before reading child tables.
- File, chunk, embedding, citation, dependency, and architecture records must be validated as belonging to the authorized repository.
- Chat requests must verify that `chat_sessions.user_id` and `chat_sessions.repository_id` are accessible to the caller.
- Index status must expose only `indexing_jobs` for repositories the caller can access.
- Security logs should record actions in `audit_logs`; do not introduce a separate legacy audit-event table.
- AI answer evidence must use `citations`; do not introduce a separate legacy source-reference table.
- Repository indexing state must use `indexing_jobs`; do not introduce a separate legacy analysis-job table.

## 1. Authentication Strategy

RepoMind AI should support secure authentication for individual users first, while preserving a path to enterprise SSO.

Initial authentication:

- GitHub OAuth for user sign-in.
- Secure server-managed session after OAuth callback.
- Optional future API key authentication for programmatic access.

Future authentication:

- Google OAuth.
- SAML SSO for enterprise customers.
- OpenID Connect for enterprise identity providers.
- Organization-level enforced SSO.

Authentication requirements:

- Use OAuth state parameters to prevent login CSRF.
- Use PKCE where supported by the OAuth flow.
- Verify provider identity using stable provider user IDs.
- Normalize and verify email addresses before using them for account identity.
- Support account suspension and revocation.
- Record login events in audit logs.
- Use secure redirect URI allowlists.
- Avoid exposing provider tokens to the browser.

Authentication failure behavior:

- Return safe, generic errors for invalid credentials or denied access.
- Rate limit repeated login attempts.
- Log authentication failures with request ID, IP, user agent, provider, and safe reason code.
- Do not reveal whether an email address exists when future email-based auth is introduced.

## 2. Authorization (RBAC)

Authorization must be enforced server-side for every protected resource.

Initial authorization model:

- User owns or connects repositories.
- Repository access is checked before any repository detail, file, chunk, embedding, chat, citation, dependency graph, or architecture snapshot is returned.
- API keys inherit scoped permissions from the user or organization that created them.

Future RBAC model:

| Role | Intended Permissions |
| --- | --- |
| `owner` | Full workspace administration, billing, member management, repository management, security settings. |
| `admin` | Manage repositories, users, indexing, integrations, and audit visibility. |
| `maintainer` | Connect repositories, start indexing, view repository intelligence, manage repository settings. |
| `developer` | View authorized repositories, use chat, search, files, summaries, and graphs. |
| `viewer` | Read-only access to authorized repository intelligence. |
| `billing_admin` | Billing and subscription management only. |

Authorization rules:

- Check authorization in application services, not only HTTP handlers.
- Use centralized policy functions for repository, chat, file, admin, billing, and API key actions.
- Deny by default.
- Do not trust frontend route hiding as access control.
- Ensure child resources belong to the parent repository before returning them.
- Avoid leaking resource existence through error messages when access is denied.
- Audit sensitive authorization failures and administrative actions.

Recommended policy examples:

- `repository:read`
- `repository:index`
- `repository:manage`
- `file:read`
- `chat:read`
- `chat:write`
- `architecture:read`
- `dependency_graph:read`
- `api_key:create`
- `api_key:revoke`
- `billing:manage`
- `admin:audit_read`

## 3. JWT and Session Handling

Browser sessions should use secure, HTTP-only cookies. JWTs may be used internally or for non-browser clients only when there is a clear need.

Session cookie requirements:

- `HttpOnly` enabled.
- `Secure` enabled in all non-local environments.
- `SameSite=Lax` by default, or `Strict` where compatible with OAuth flow.
- Short access/session lifetime.
- Refresh or rolling session strategy with rotation.
- Server-side session invalidation support.
- Session ID stored hashed server-side if persisted.

JWT requirements if introduced:

- Use asymmetric signing for multi-service environments.
- Keep JWT lifetime short.
- Include minimal claims.
- Validate issuer, audience, expiration, not-before, and signature.
- Do not store secrets, provider tokens, or sensitive repository data in JWT claims.
- Support key rotation with key IDs.
- Maintain revocation strategy for compromised tokens.

Refresh requirements:

- Rotate refresh tokens.
- Detect refresh token reuse.
- Store refresh tokens hashed.
- Revoke all sessions on suspected compromise.
- Audit refresh failures and suspicious patterns.

## 4. API Security

All APIs must assume hostile input and unauthorized access attempts.

API security requirements:

- Require HTTPS in deployed environments.
- Enforce authentication on all protected endpoints.
- Validate request body, query parameters, path parameters, and headers.
- Use centralized error handling.
- Return consistent safe error responses.
- Use request IDs for traceability.
- Enforce CORS allowlists.
- Limit request body size.
- Limit chat message size and search query length.
- Limit repository indexing frequency and repository size.
- Use strict content types for JSON APIs.
- Apply rate limits by IP, user, API key, and repository where appropriate.
- Do not expose stack traces or internal dependency errors.

Recommended security headers:

- `Content-Security-Policy`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY` or CSP `frame-ancestors`
- `Referrer-Policy`
- `Permissions-Policy`
- `Strict-Transport-Security` in production

API key requirements:

- Show API keys only once at creation.
- Store only cryptographic hashes of API keys.
- Use key prefixes for lookup and display.
- Support scopes and expiration.
- Support revocation.
- Audit creation, use, and revocation.

## 5. Rate Limiting

Rate limiting protects users, infrastructure, external providers, and AI costs.

Rate limit dimensions:

- IP address.
- Authenticated user ID.
- API key ID.
- Repository ID.
- Organization ID in future enterprise mode.
- Endpoint category.

Endpoints requiring strict limits:

- Login and OAuth callback.
- Token refresh.
- Repository indexing.
- Semantic search.
- AI chat.
- File explanation.
- Architecture generation.
- API key creation.

Rate limiting behavior:

- Return `429 Too Many Requests`.
- Include safe retry metadata such as retry-after seconds.
- Use stricter limits for unauthenticated endpoints.
- Use cost-aware limits for AI endpoints.
- Log repeated rate limit violations.
- Consider temporary blocks for abuse patterns.

Future protections:

- Adaptive rate limits by plan.
- Organization-level token and indexing budgets.
- Abuse detection for automated scraping or prompt flooding.

## 6. Input Validation

All input must be validated before use.

Validation layers:

- Frontend validation for usability.
- Backend request schema validation for security.
- Application service validation for business rules.
- Database constraints for integrity.

Inputs to validate:

- OAuth provider values.
- Redirect URIs.
- Repository owner and name.
- Provider repository IDs.
- Branch names.
- File IDs and repository IDs.
- Pagination cursors and limits.
- Search queries.
- Chat messages.
- File paths.
- API key names and scopes.
- Billing and admin actions.
- Webhook payloads.

Validation rules:

- Use allowlists for enum-like values.
- Bound string lengths.
- Bound numeric ranges.
- Reject unexpected fields where practical.
- Normalize emails, repository names, and paths carefully.
- Validate file paths to prevent traversal.
- Validate JSON payload size and structure.
- Reject null bytes and unsafe control characters in path-like input.

## 7. SQL Injection Prevention

SQL injection must be prevented through query parameterization and disciplined data access.

Requirements:

- Use SQLAlchemy parameter binding or equivalent safe query APIs.
- Do not build SQL strings from user input.
- Avoid dynamic `ORDER BY`, table names, or column names unless values are allowlisted.
- Use parameterized full-text search queries.
- Validate vector search filters before query construction.
- Review raw SQL manually when it is unavoidable.
- Keep database user permissions limited to required operations.

High-risk areas:

- Search filters.
- Sorting parameters.
- Admin audit queries.
- Dynamic repository filters.
- JSONB metadata filters.
- Vector search metadata constraints.

Testing expectations:

- Add negative tests for malicious query inputs when implementation begins.
- Include validation tests for filters, sort fields, and pagination cursors.
- Run static analysis or security linters where available.

## 8. XSS and CSRF Protection

RepoMind AI will display source code, AI responses, markdown-like summaries, repository metadata, file paths, and user-generated chat content. These must be treated as untrusted.

XSS protections:

- Escape user-controlled content by default.
- Sanitize rendered markdown.
- Use a strict allowlist for markdown elements.
- Do not render raw HTML from AI responses or repository files.
- Treat repository file content as text, not executable markup.
- Use syntax highlighting libraries safely.
- Avoid dangerous frontend APIs for HTML insertion.
- Apply a restrictive Content Security Policy.

AI-specific XSS concerns:

- AI responses may contain malicious-looking HTML, script tags, or links because repository content can contain them.
- Render AI output through sanitized markdown or plain text.
- Mark external links clearly and use safe link attributes.

CSRF protections:

- Use `SameSite` cookies.
- Use CSRF tokens for state-changing browser requests if cookie auth is used.
- Validate OAuth `state`.
- Restrict CORS origins.
- Require JSON content type for state-changing API requests.
- Do not allow credentialed cross-origin requests except from approved app origins.

## 9. Secret Management

Secrets must never be hardcoded, committed, logged, or exposed to clients.

Secret categories:

- GitHub OAuth client secret.
- GitHub access and refresh tokens.
- OpenAI API keys.
- Database credentials.
- Redis credentials.
- Session signing keys.
- Encryption keys.
- Billing provider secrets.
- Webhook signing secrets.

Secret management requirements:

- Store secrets in environment variables or a managed secret store.
- Validate required secrets at startup.
- Use separate secrets for development, staging, and production.
- Rotate secrets periodically and after suspected exposure.
- Restrict secret access by service role.
- Never print secrets in logs, error responses, traces, or analytics.
- Keep `.env.example` free of real values.
- Avoid sharing production secrets with local development.

Rotation requirements:

- Document rotation steps for each secret type.
- Support overlapping keys where needed for zero-downtime rotation.
- Audit secret access through the deployment platform or secret manager.

## 10. GitHub OAuth Security

GitHub OAuth introduces identity, repository access, and token storage risks.

Requirements:

- Use exact redirect URI allowlists.
- Use OAuth state for CSRF protection.
- Use PKCE if supported by the selected flow.
- Request the minimum required scopes.
- Store provider tokens encrypted at rest.
- Never return provider tokens to the frontend.
- Track token scopes and expiration.
- Support disconnect and token revocation.
- Revalidate repository access before indexing.
- Handle provider access revocation gracefully.
- Verify webhook signatures when webhooks are introduced.

Scope strategy:

- Start with the minimum scope required to read selected repositories.
- Prefer GitHub App installation permissions for repository access as the product matures.
- Avoid broad organization access unless explicitly required and approved.

Risk controls:

- Audit repository connection, disconnection, and indexing events.
- Avoid logging repository clone URLs containing credentials.
- Use provider IDs rather than mutable names for stable identity.
- Respect GitHub rate limits and abuse detection guidance.

## 11. OpenAI API Key Protection

AI provider credentials must be protected as production secrets.

Requirements:

- Store OpenAI API keys only in backend or worker runtime secrets.
- Never expose AI provider keys to the browser.
- Never commit AI provider keys.
- Restrict provider key access to services that need model calls.
- Use separate keys per environment.
- Monitor token usage and errors.
- Set budget alerts where supported.
- Rotate keys after suspected exposure.
- Avoid logging full prompts when they contain private repository data.
- Redact or minimize repository content in traces.

AI data protection:

- Treat prompts, retrieved chunks, embeddings, and generated responses as sensitive.
- Clearly document provider data handling and retention behavior before production launch.
- Offer enterprise controls for model provider selection and data retention when needed.
- Keep model names configurable, not hardcoded.

## 12. Database Security

Database security must protect product data, repository intelligence, tokens, embeddings, chat history, and audit logs.

Requirements:

- Use TLS for database connections in deployed environments.
- Use managed PostgreSQL encryption at rest.
- Encrypt highly sensitive fields at the application layer where appropriate.
- Store API keys as hashes only.
- Store OAuth tokens encrypted, never plaintext.
- Use least-privilege database users.
- Separate migration role from runtime application role where practical.
- Restrict database network access.
- Enable automated backups and point-in-time recovery.
- Monitor slow queries and suspicious access patterns.
- Avoid production data in local development.

Sensitive tables:

- `users`
- `user_profiles`
- `api_keys`
- `repositories`
- `repository_branches`
- `indexing_jobs`
- OAuth token storage table when introduced.
- `repository_files`
- `code_chunks`
- `embeddings`
- `chat_sessions`
- `chat_messages`
- `citations`
- `dependency_edges`
- `architecture_snapshots`
- `audit_logs`

Access control:

- Application-level authorization remains mandatory even if database row-level security is introduced later.
- Future enterprise versions may use row-level security for tenant isolation after operational maturity.

## 13. File Upload Security

RepoMind AI may ingest repositories through GitHub initially and may later support direct archive uploads. Both paths require safeguards.

Repository ingestion safeguards:

- Enforce repository size limits.
- Enforce file size limits.
- Detect and skip binary files where appropriate.
- Exclude ignored directories such as dependency folders, build output, and generated artifacts.
- Detect possible secrets and avoid indexing known secret files.
- Normalize file paths.
- Prevent path traversal.
- Treat all file content as untrusted text.

Direct upload safeguards, if introduced:

- Accept only explicitly allowed archive formats.
- Scan archive entries before extraction.
- Prevent zip-slip path traversal.
- Enforce decompressed size limits.
- Enforce file count limits.
- Store uploads in isolated temporary storage.
- Run malware scanning where customer risk requires it.
- Delete temporary files after processing.
- Do not execute uploaded code.

File display safeguards:

- Render source files as escaped text.
- Do not execute repository HTML, scripts, notebooks, or SVGs in the application origin.
- Use safe previews for binary and rich file formats.

## 14. Logging and Auditing

Logging and auditing must support debugging, incident response, compliance, and user trust.

Logging requirements:

- Use structured logs.
- Include request IDs.
- Include user ID and repository ID when safe and applicable.
- Log authentication events, authorization failures, indexing lifecycle, provider errors, AI provider failures, and admin actions.
- Redact secrets, tokens, API keys, cookies, authorization headers, and private source content.
- Avoid logging full prompts and full AI responses in production.

Audit log events:

- User login and logout.
- OAuth connection and disconnection.
- Repository connection.
- Repository indexing started, completed, failed, cancelled, or retried.
- Chat session creation.
- API key creation and revocation.
- Billing changes.
- Admin actions.
- Permission changes.
- Security setting changes.

Audit log requirements:

- Append-only behavior.
- Tamper-resistant storage strategy for enterprise customers.
- Retention policy by plan or organization.
- Export support for enterprise customers.
- Safe metadata only.

## 15. Backup and Disaster Recovery

RepoMind AI must be recoverable after database failure, accidental deletion, deployment failure, or provider outage.

Backup requirements:

- Automated database backups.
- Point-in-time recovery.
- Backup encryption at rest.
- Backup access restricted by least privilege.
- Restore testing on a regular schedule.
- Separate backup retention policies for production and staging.

Disaster recovery requirements:

- Define recovery point objective.
- Define recovery time objective.
- Document database restore procedure.
- Document application rollback procedure.
- Document secret rotation procedure after incident.
- Document provider outage behavior.
- Monitor backup success and restore test success.

Data recovery priorities:

- User and authorization data.
- Repository records and indexing metadata.
- Audit logs.
- Chat history and citations.
- Code chunks and embeddings, depending on whether they can be regenerated safely and quickly.

Operational considerations:

- Embeddings may be regenerable but expensive.
- Repository chunks may be regenerable only if provider access and commit history remain available.
- Audit logs should have stronger retention and integrity guarantees than cache-like derived artifacts.

## 16. OWASP Top 10 Considerations

### A01: Broken Access Control

Controls:

- Centralized authorization policies.
- Repository-scoped access checks.
- Child resource ownership validation.
- Deny by default.
- Tests for forbidden repository, file, chat, and admin access.

### A02: Cryptographic Failures

Controls:

- TLS everywhere in production.
- Encryption at rest for managed databases and backups.
- Application-level encryption for provider tokens.
- Secure passwordless OAuth flow.
- Strong secret generation and rotation.

### A03: Injection

Controls:

- Parameterized database queries.
- Strict request validation.
- Allowlisted sort and filter fields.
- Sanitized full-text and vector-search filters.
- No shell execution of repository-controlled input.

### A04: Insecure Design

Controls:

- Threat modeling before high-risk features.
- Security requirements documented before implementation.
- Explicit abuse cases for AI chat, indexing, OAuth, and file rendering.
- Secure architecture reviews before production launch.

### A05: Security Misconfiguration

Controls:

- Environment-specific configuration validation.
- Secure headers.
- Restrictive CORS.
- No debug mode in production.
- Managed secrets.
- Infrastructure hardening checklist.

### A06: Vulnerable and Outdated Components

Controls:

- Dependency scanning.
- Automated dependency updates.
- Lockfiles.
- Regular patch cadence.
- Review of AI, OAuth, markdown, syntax highlighting, and file parsing libraries.

### A07: Identification and Authentication Failures

Controls:

- Secure session cookies.
- OAuth state validation.
- Session rotation.
- Token revocation.
- Rate-limited login and refresh.
- Audit suspicious authentication failures.

### A08: Software and Data Integrity Failures

Controls:

- CI checks before deployment.
- Signed or verified deployment artifacts where practical.
- Reviewed migrations.
- Webhook signature verification.
- No execution of repository code during indexing.

### A09: Security Logging and Monitoring Failures

Controls:

- Structured security logs.
- Audit logs for sensitive actions.
- Alerting for repeated auth failures, provider errors, rate limit abuse, and admin actions.
- Request IDs across API and workers.

### A10: Server-Side Request Forgery

Controls:

- Allowlist repository providers.
- Validate provider URLs.
- Do not fetch arbitrary user-provided URLs.
- Restrict outbound network access where possible.
- Block internal IP ranges for any future URL ingestion feature.

## 17. Security Checklist Before Deployment

Authentication and sessions:

- GitHub OAuth state validation is implemented.
- Redirect URI allowlist is configured.
- Session cookies use `HttpOnly`, `Secure`, and appropriate `SameSite`.
- Session expiration and revocation are implemented.
- Login and refresh endpoints are rate limited.

Authorization:

- Repository access checks are enforced server-side.
- Child resources are validated against parent repository access.
- Admin and billing routes require explicit permissions.
- API keys have scopes and revocation.

API and validation:

- All request bodies, query parameters, and path parameters are validated.
- Request body size limits are configured.
- Standard error responses do not leak internals.
- CORS allowlist is configured.
- Security headers are configured.

Secrets:

- No secrets are committed.
- Production secrets are stored in a managed secret system.
- OpenAI API keys are backend-only.
- GitHub tokens are encrypted at rest.
- Secret rotation procedure is documented.

Database:

- Database uses TLS in production.
- Backups and point-in-time recovery are enabled.
- Runtime database user has least privilege.
- Migrations are reviewed and tested.
- Sensitive fields are encrypted or hashed as appropriate.

Repository ingestion and files:

- Repository size and file size limits are enforced.
- Binary and generated files are handled safely.
- Path traversal protections are implemented.
- Repository content is rendered as escaped text.
- Secret-like files are excluded or handled through a documented policy.

AI security:

- Prompts and retrieved repository context are treated as sensitive.
- AI provider keys are not exposed to clients.
- Full private source content is not logged.
- AI responses are sanitized before rendering.
- Repository-specific AI claims include citations where required.

Logging and monitoring:

- Structured logs include request IDs.
- Sensitive values are redacted.
- Audit logs exist for security-sensitive actions.
- Alerting is configured for authentication abuse, provider failures, and indexing failures.

Backup and recovery:

- Automated backups are enabled.
- Restore procedure has been tested.
- Recovery point objective and recovery time objective are documented.
- Incident response and rollback procedures are documented.

OWASP review:

- OWASP Top 10 review has been completed.
- High-risk findings are resolved or explicitly accepted.
- Security tests are included in CI where practical.

The product should not be deployed to production until this checklist is complete or any exceptions are documented, risk-assessed, and approved.
