# RepoMind AI UI/UX Specification

## Purpose

This document defines the complete user experience direction for RepoMind AI. It is documentation only and does not introduce application code, components, routes, styles, or assets.

RepoMind AI should feel like a serious engineering workspace: calm, fast, information-dense, trustworthy, and built for repeated daily use by developers and engineering leaders.

## Experience Principles

- Prioritize repository understanding over visual spectacle.
- Make citations, confidence, and provenance visible.
- Keep long-running analysis states clear and predictable.
- Use layouts that support scanning, comparison, and investigation.
- Keep primary workflows available within one or two clicks.
- Avoid hiding important system state behind decorative UI.
- Preserve user trust through transparent empty, loading, and error states.
- Design for keyboard-friendly workflows and accessible contrast.

## Information Architecture

Primary navigation:

- Dashboard
- Repositories
- Chat
- Architecture
- Dependency Graph
- Settings
- Billing
- Admin

Repository-scoped navigation:

- Overview
- Chat
- Files
- Architecture
- Dependencies
- Indexing Status
- Settings

Global utility navigation:

- Search
- Notifications
- Help
- User menu
- Workspace switcher, when organizations are introduced

## Global Layout Model

Authenticated application layout:

- Left sidebar for primary navigation.
- Top bar for workspace context, global search, notifications, and user menu.
- Main content area for page-specific workflows.
- Optional right inspection panel for details, citations, filters, or metadata.

Repository workspace layout:

- Repository header with name, provider, branch selector, latest index status, and actions.
- Repository-scoped tabs or secondary navigation.
- Main panel for selected workflow.
- Optional resizable side panel for file preview, citations, or graph details.

## Visual Design System

### Color Palette

The palette should communicate focus, reliability, and technical clarity without becoming visually cold or monotone.

Core colors:

| Token | Suggested Value | Usage |
| --- | --- | --- |
| `background` | `#F7F8FA` | Main app background. |
| `surface` | `#FFFFFF` | Primary panels, cards, tables. |
| `surface-muted` | `#F1F4F8` | Secondary panels and subtle grouped areas. |
| `border` | `#D8DEE8` | Dividers, panel borders, table lines. |
| `text-primary` | `#17202A` | Primary body text and headings. |
| `text-secondary` | `#516173` | Supporting text and metadata. |
| `text-muted` | `#7A8797` | Timestamps, placeholders, inactive labels. |
| `accent` | `#2563EB` | Primary actions, active navigation, links. |
| `accent-hover` | `#1D4ED8` | Hover state for primary actions. |
| `success` | `#168A4A` | Completed indexing, healthy status. |
| `warning` | `#B7791F` | Partial analysis, degraded state. |
| `danger` | `#C2413A` | Errors, destructive actions. |
| `info` | `#0F766E` | Informational highlights and repository insights. |
| `code-bg` | `#0F172A` | Code preview background when dark code blocks are used. |

Usage rules:

- Use accent color sparingly for active controls and primary calls to action.
- Use semantic colors consistently for status and alerts.
- Avoid large gradient backgrounds in authenticated product areas.
- Preserve contrast for code, tables, graphs, and dense metadata.
- Use neutral surfaces and borders to keep engineering workflows readable.

### Dark and Light Mode

RepoMind AI supports light, dark, and system-preference modes using a class-based theme strategy. The design should feel close to developer tools such as GitHub: neutral surfaces, crisp borders, compact navigation, readable code-oriented content, and restrained use of color.

Theme behavior:

- Default to the user's system preference when no explicit selection exists.
- Persist the user's selected theme across refreshes and future sessions.
- Apply theme changes without a page reload.
- Keep all text, icons, borders, controls, and cards readable in both modes.
- Avoid theme-specific business logic; theme state is a UI preference only.

Theme toggle behavior:

- Place the toggle in the global top navigation.
- Use a moon icon when the next action is switching to dark mode.
- Use a sun icon when the next action is switching to light mode.
- Provide an accessible `aria-label` that describes the action.
- Preserve keyboard focus visibility and pointer hover states.

GitHub-inspired layout direction:

- Use a compact top navbar with RepoMind AI branding, global search, sign-in, get-started, dashboard, logout, and theme controls as appropriate to auth state.
- Use repository-style preview cards, file/module rows, and status pills to make the product category obvious.
- Keep the landing page branded as RepoMind AI; do not use GitHub logos, GitHub-owned copy, or provider branding as decoration.
- Prefer operational UI previews over abstract illustrations.

### Typography

Recommended font approach:

- UI font: Inter, system UI, or an equivalent modern sans-serif.
- Code font: JetBrains Mono, SFMono-Regular, Consolas, or an equivalent monospace.

Type scale:

| Role | Size | Weight | Usage |
| --- | --- | --- | --- |
| Page title | 28px | 650 | Primary page heading. |
| Section title | 20px | 650 | Main sections. |
| Panel title | 16px | 600 | Cards, sidebars, modals. |
| Body | 14px | 400 | Default application text. |
| Metadata | 12px | 400 | Labels, timestamps, secondary status. |
| Code | 13px | 400 | File previews and snippets. |

Typography rules:

- Keep line length readable in summaries and chat answers.
- Use monospace only for code, file paths, branch names, hashes, and commands.
- Avoid oversized headings inside operational pages.
- Keep labels concise and scannable.

### Icon Style

Icon direction:

- Use simple outline icons with consistent stroke weight.
- Prefer familiar symbols for common actions: search, settings, upload, refresh, branch, file, folder, lock, alert, check, copy, external link.
- Use provider icons for GitHub and future repository providers.
- Pair unfamiliar icons with tooltips.
- Keep icon-only buttons accessible through labels and tooltips.

Recommended icon characteristics:

- 16px icons inside compact controls.
- 20px icons inside primary navigation and larger buttons.
- 1.75px to 2px stroke width.
- No decorative icon clusters that distract from repository data.

### Responsive Behavior

Desktop:

- Use full left navigation and multi-panel layouts.
- Support side-by-side chat and citations.
- Support file tree plus file preview.
- Support graph canvas with inspector panel.

Tablet:

- Collapse sidebar to icons or drawer.
- Stack secondary panels below primary content when width is limited.
- Keep repository header and branch selector visible.

Mobile:

- Use bottom or drawer navigation for primary areas.
- Prefer single-column workflows.
- File tree, filters, and inspectors should open as sheets.
- Chat input should remain accessible without covering message content.
- Large graphs should show simplified controls and pan/zoom gestures.

Accessibility:

- All interactive elements must be keyboard reachable.
- Focus states must be visible.
- Color must not be the only indicator of state.
- Loading and error states should be announced to assistive technologies where possible.

## Page Specifications

## 1. Landing Page

### Purpose

Introduce RepoMind AI to unauthenticated visitors and convert qualified users to sign in or request access.

### Components

- Global top navigation with RepoMind AI branding, search, theme toggle, sign-in, and get-started actions.
- Hero section with product name, concise value proposition, and primary action.
- Repository intelligence preview using real product concepts such as chat, citations, indexing status, and architecture summary.
- Problem and value sections.
- Feature sections for repository Q&A, onboarding, dependency understanding, and review assistance.
- Security and privacy section.
- Pricing or early access section.
- Footer with legal, docs, status, and contact links.

### Layout

- Full-width marketing layout.
- First viewport should make the product category obvious.
- Hero should show a concrete repository intelligence interface preview, not abstract decoration.
- Later sections should alternate concise copy with product screenshots or diagrams.

### Navigation

- Primary actions: Sign in, get started, and view dashboard when authenticated.
- Secondary links: Docs, pricing, security, GitHub integration.
- Signed-in users should be redirected to Dashboard from primary app entry points.

### User Interactions

- Start sign-in flow.
- Request early access or demo.
- Navigate to documentation.
- View security or pricing details.

### Empty States

- Not applicable for primary marketing content.
- If pricing or demo scheduling is unavailable, show a contact fallback.

### Loading States

- Sign-in button shows progress during auth flow initialization.
- Demo request form shows submitting state.

### Error States

- Auth initialization failure with retry action.
- Demo request validation errors.
- Network failure message with support contact.

## 2. Login

### Purpose

Allow users to authenticate securely and enter the product.

### Components

- Product logo and short trust-oriented message.
- Google sign-in button.
- Disabled GitHub sign-in placeholder until GitHub OAuth is implemented in a later sprint.
- Terms and privacy links.
- Error alert area.

### Layout

- Centered authentication panel on a quiet background.
- Keep form narrow and focused.
- Avoid marketing-heavy content on this page.

### Navigation

- Back to landing page.
- Continue to Google OAuth.
- Redirect to intended destination after login.

### User Interactions

- Click Google sign-in.
- Retry after failed login.
- Open terms or privacy links.

### Empty States

- If no auth providers are configured in an environment, show a configuration unavailable message.

### Loading States

- Disable sign-in button while login URL is being requested.
- Show redirecting state before provider handoff.

### Error States

- OAuth provider unavailable.
- Invalid or expired OAuth state.
- User denied provider authorization.
- Account suspended or not allowed.

## 3. Dashboard

### Purpose

Give users a concise command center for repository activity, recent analysis, ongoing jobs, and recommended next actions.

### Components

- Welcome header with workspace context.
- Recent repositories list.
- Active indexing jobs panel.
- Recent chat sessions.
- Repository health or coverage summary.
- Suggested actions such as connect repository, resume chat, view failed jobs.
- Usage snapshot for indexed repositories, chat messages, and token usage.

### Layout

- Two-column desktop layout.
- Main column: recent repositories and activity.
- Side column: active jobs, usage, and quick actions.
- Mobile layout stacks panels by priority.

### Navigation

- Global navigation to Repositories, Chat, Settings, Billing.
- Repository cards link to Repository Details.
- Active jobs link to Index Status.

### User Interactions

- Connect a new repository.
- Resume a chat session.
- Open repository details.
- Retry failed indexing job.
- Dismiss non-critical recommendations.

### Empty States

- No repositories connected: show connect GitHub action and a short explanation of what indexing enables.
- No recent chats: suggest asking the first repository question after indexing.
- No jobs: show a calm idle state.

### Loading States

- Skeleton panels for repository cards, jobs, and recent chats.
- Inline loading for retry actions.

### Error States

- Failed to load dashboard data.
- Partial failure when repositories load but job status does not.
- Permission changes causing previously visible repository cards to become inaccessible.

## 4. Repository List

### Purpose

Help users browse, search, filter, and connect repositories.

### Components

- Page header with connect repository action.
- Search input.
- Provider filter.
- Indexing status filter.
- Repository table or list.
- Pagination controls.
- Bulk or batch actions in future.

### Layout

- Dense table on desktop with columns for repository, provider, visibility, default branch, last indexed, latest status, and actions.
- Card list on mobile.
- Filters above the list.

### Navigation

- Repository row opens Repository Details.
- Connect GitHub opens repository connection flow.
- Status links to indexing detail.

### User Interactions

- Search repositories.
- Filter by provider or status.
- Sort by name, updated time, or index status.
- Connect GitHub repository.
- Start or retry indexing.

### Empty States

- No connected repositories: show connect GitHub action.
- No search results: show filter reset action.
- No repositories match current status: suggest clearing filters.

### Loading States

- Table skeleton rows.
- Search debounce loading indicator.
- Button-level loading for connect and index actions.

### Error States

- Failed to load repositories.
- GitHub provider unavailable.
- Access revoked for connected repository.

## 5. Repository Details

### Purpose

Provide an overview of a single repository, its indexing state, summary, branches, important files, and navigation into deeper analysis.

### Components

- Repository header with provider, owner/name, visibility, branch selector, and latest indexing status.
- Summary panel.
- Indexing status panel.
- Key directories and entry points.
- Technology detection.
- Recent chats.
- Recent indexing jobs.
- Quick actions: start indexing, open chat, view files, view architecture, view dependency graph.

### Layout

- Header fixed to top of repository context.
- Main grid with summary and operational state.
- Secondary panels for technology, activity, and entry points.

### Navigation

- Repository tabs: Overview, Chat, Files, Architecture, Dependencies, Indexing.
- Breadcrumb from Repositories to current repository.
- File and citation links open File Explorer.

### User Interactions

- Switch branch.
- Start indexing or re-indexing.
- Open generated summary citations.
- Navigate to chat or file explorer.
- Retry failed indexing job.

### Empty States

- Repository connected but not indexed: show start indexing action.
- Indexing in progress: show progress and explain what becomes available afterward.
- No summary available: show pending analysis state.

### Loading States

- Header metadata skeleton.
- Summary skeleton.
- Indexing progress indicator.
- Branch selector loading state.

### Error States

- Repository not found or access denied.
- Indexing failed with safe error reason and retry action.
- Provider access revoked.
- Summary generation failed.

## 6. Repository Chat

### Purpose

Allow users to ask repository-grounded questions and receive cited, verifiable answers.

### Components

- Chat session list.
- Conversation message pane.
- Message composer.
- Citation panel.
- Repository and branch context selector.
- Suggested starter questions.
- Response feedback controls.
- Source preview drawer or side panel.

### Layout

- Desktop: session list on left, conversation center, citations or file preview on right.
- Tablet: session list collapses; citations panel becomes drawer.
- Mobile: single conversation view with session drawer and citation sheet.

### Navigation

- Repository tabs remain available.
- Citation links navigate to file preview at cited lines.
- Session list navigates between conversations.

### User Interactions

- Create new chat session.
- Send message.
- Open citations.
- Copy answer.
- Provide thumbs-up or thumbs-down feedback.
- Rename or archive chat session.
- Switch branch before starting a new session.

### Empty States

- No chat sessions: show starter questions based on repository summary.
- Repository not indexed: explain that chat requires indexing and offer start indexing.
- No citations for a general answer: clearly label the answer as general guidance.

### Loading States

- Assistant typing or generating state.
- Retrieval state before answer generation.
- Streaming message support in future.
- Citation panel skeleton while sources load.

### Error States

- AI provider unavailable.
- Repository context insufficient.
- Message exceeds length limit.
- Chat session not found.
- Access denied after repository permission change.

## 7. File Explorer

### Purpose

Let users browse indexed repository files, read source content, inspect chunks, and request file explanations.

### Components

- File tree.
- Path search.
- Language and folder filters.
- File preview with syntax highlighting.
- Metadata header with path, language, size, hash, and indexed time.
- Explain file action.
- Chunk and citation markers.
- Dependency references for selected file.

### Layout

- Desktop: file tree left, code preview center, metadata/explanation panel right.
- Tablet: tree collapses into drawer.
- Mobile: file list first, file content opens in full-screen view.

### Navigation

- Breadcrumb path navigation.
- Repository tabs.
- Links from citations and search results open the file and scroll to line range.

### User Interactions

- Expand and collapse folders.
- Search by path.
- Select file.
- Copy file path.
- Open provider web URL.
- Explain file.
- Jump to cited lines.

### Empty States

- Repository not indexed: show start indexing action.
- No files match filter: show clear filters action.
- Binary file selected: show metadata only and explain why content is unavailable.

### Loading States

- File tree skeleton.
- Code preview loading state.
- Explain file generation state.
- Lazy folder loading in large repositories.

### Error States

- File not found.
- File too large to display.
- Failed to load file content.
- Explanation unavailable due to AI provider error.

## 8. Architecture Viewer

### Purpose

Show generated architecture summaries, module maps, and high-level system diagrams for a repository.

### Components

- Architecture summary panel.
- Diagram canvas or rendered Mermaid view.
- Module list.
- Technology stack panel.
- Entry points panel.
- Risks and unknowns panel.
- Snapshot selector.
- Source citations.

### Layout

- Main diagram area with controls.
- Right inspection panel for selected module or citation.
- Summary and risks below or beside the diagram depending on viewport.

### Navigation

- Repository tabs.
- Module clicks navigate to related files or dependency graph.
- Citation clicks open File Explorer.

### User Interactions

- Select architecture snapshot.
- Zoom and pan diagram.
- Select module.
- Toggle diagram layers.
- Copy Mermaid diagram.
- Open related files.

### Empty States

- Architecture snapshot unavailable: show analysis requirement and index action.
- No module structure detected: explain limitations and show available summary.

### Loading States

- Diagram skeleton.
- Snapshot loading indicator.
- Module list placeholder.

### Error States

- Snapshot generation failed.
- Diagram rendering failed.
- Selected snapshot is stale compared with current branch index.

## 9. Dependency Graph

### Purpose

Visualize relationships between files, modules, packages, and external dependencies to support impact analysis and codebase understanding.

### Components

- Graph canvas.
- Scope selector: repository, folder, file.
- Depth control.
- Dependency type filters.
- External dependency toggle.
- Search within graph.
- Selected node inspector.
- Edge details panel.
- Export option in future.

### Layout

- Full-width graph workspace.
- Top toolbar for filters and graph controls.
- Right inspector for selected node or edge.
- Mobile uses simplified list plus focused graph view.

### Navigation

- Repository tabs.
- Node click opens inspector.
- File node action opens File Explorer.
- Module node action opens Architecture Viewer.

### User Interactions

- Pan and zoom.
- Select node or edge.
- Filter dependency types.
- Change graph depth.
- Search for file or module.
- Toggle external dependencies.
- Reset layout.

### Empty States

- Graph unavailable until indexing completes.
- No dependencies detected for selected scope.
- Filters hide all nodes: show reset filters action.

### Loading States

- Graph loading overlay.
- Progressive rendering for large graphs.
- Toolbar controls disabled while graph data loads.

### Error States

- Dependency graph failed to load.
- Graph too large for selected depth, requiring narrower scope.
- Unsupported language relationships for selected repository.

## 10. Settings

### Purpose

Allow users to manage account preferences, connected providers, security, notifications, and future workspace settings.

### Components

- Profile settings.
- Connected accounts.
- GitHub connection status.
- Session management.
- API keys.
- Notification preferences.
- Data and privacy controls.
- Danger zone for account deletion or provider disconnect.

### Layout

- Settings sidebar with sections.
- Main settings form area.
- Save actions scoped per section.
- Dangerous actions visually separated.

### Navigation

- Global navigation to Settings.
- Section anchors or tabs within settings.
- Links to billing and admin when user has access.

### User Interactions

- Update display name, timezone, and locale.
- Connect or disconnect GitHub.
- Create, revoke, or rename API keys.
- Manage active sessions.
- Update notification preferences.
- Request account deletion.

### Empty States

- No API keys: show create key action.
- No connected providers: show connect GitHub action.
- No active sessions beyond current session: show current session only.

### Loading States

- Form save progress.
- Provider connection verification.
- API key creation progress.

### Error States

- Failed to save preferences.
- Provider disconnect blocked by active repositories.
- Invalid API key name or scope.
- Account deletion confirmation mismatch.

## 11. Billing

### Purpose

Show plan, usage, invoices, payment methods, and upgrade controls.

### Components

- Current plan summary.
- Usage metrics: repositories indexed, tokens used, seats, storage, API calls.
- Billing period progress.
- Plan comparison.
- Payment method section.
- Invoice history.
- Upgrade, downgrade, or cancel actions.

### Layout

- Plan and usage summary at top.
- Usage breakdown panels.
- Billing details and invoices below.
- Plan comparison in modal or dedicated section.

### Navigation

- Global navigation to Billing.
- Links to settings for account details.
- Admin-only billing controls for organization plans.

### User Interactions

- View usage.
- Update payment method.
- Download invoice.
- Upgrade or change plan.
- Cancel subscription with confirmation.

### Empty States

- Free plan with no usage: show what usage will appear after connecting repositories.
- No invoices yet: show billing cycle start date.
- No payment method required for free plan.

### Loading States

- Usage metrics skeleton.
- Payment provider loading state.
- Invoice list loading state.

### Error States

- Billing provider unavailable.
- Payment method update failed.
- Invoice download failed.
- User lacks billing permissions.

## 12. Admin Dashboard

### Purpose

Give administrators visibility and control over users, repositories, jobs, usage, audit logs, and system health.

### Components

- Admin overview metrics.
- User management table.
- Repository management table.
- Indexing job monitor.
- Usage and cost dashboard.
- Audit log viewer.
- Provider health status.
- Feature flag controls in future.

### Layout

- Admin-specific sidebar or section navigation.
- Metric cards at top.
- Operational tables below.
- Filters for user, repository, action, status, and time range.

### Navigation

- Admin link visible only to authorized users.
- Links from metrics to filtered tables.
- Audit log entries link to related resources when permitted.

### User Interactions

- Search users.
- View repository indexing status.
- Retry or cancel jobs where safe.
- Inspect audit log entries.
- Export audit logs in future.
- Disable API keys or suspend users where permitted.

### Empty States

- No audit log entries for selected filters.
- No failed jobs.
- No repositories connected in workspace.

### Loading States

- Metric skeletons.
- Table loading rows.
- Job action progress state.

### Error States

- Admin access denied.
- Failed to load audit logs.
- Failed job action due to state conflict.
- Usage metrics temporarily unavailable.

## Reusable Interaction Patterns

### Empty States

Empty states should:

- Explain what is missing.
- Explain why it matters.
- Offer one clear next action.
- Avoid blaming the user.

### Loading States

Loading states should:

- Preserve layout stability.
- Use skeletons for known content shapes.
- Use progress indicators for long-running indexing.
- Avoid indefinite spinners where job status is available.

### Error States

Error states should:

- Use safe, human-readable language.
- Include retry actions when appropriate.
- Include support-oriented request IDs for unexpected failures.
- Avoid exposing stack traces, tokens, provider secrets, or private source content.

### Confirmation Patterns

Require confirmation for:

- Disconnecting GitHub.
- Revoking API keys.
- Deleting account data.
- Cancelling paid plan.
- Retrying expensive indexing for very large repositories.

### AI Transparency Patterns

AI-generated content should:

- Show citations when repository-specific claims are made.
- Mark uncertainty clearly.
- Distinguish generated summaries from raw source.
- Offer feedback controls.
- Allow users to inspect source files behind answers.

## Responsive Priority Rules

When space is constrained:

- Keep primary task controls visible.
- Collapse navigation before hiding content.
- Move inspectors and filters into drawers or sheets.
- Prefer readable single-column workflows over cramped multi-column layouts.
- Preserve file paths and citations, even if secondary metadata is hidden.

## Product Tone

RepoMind AI should sound:

- Clear.
- Direct.
- Helpful.
- Technically credible.
- Calm under failure.

Avoid:

- Overpromising certainty.
- Cute or novelty language in operational workflows.
- Vague AI claims without citations.

## API Capability Alignment

UI pages should map cleanly to the API capabilities defined in `docs/API_SPEC.md`.

| UI page | Required API capabilities |
| --- | --- |
| Landing Page | Login initialization for signed-out conversion paths. |
| Login | Login, refresh token where needed, profile after callback. |
| Dashboard | Profile, list repositories, index status, conversation history summaries. |
| Repository List | Connect GitHub, list repositories, start indexing, index status. |
| Repository Details | Repository details, index status, repository summary, start indexing. |
| Repository Chat | Create session, send message, conversation history, read cited files. |
| File Explorer | List files, read file, explain file, keyword search. |
| Architecture Viewer | Architecture diagram, repository summary, read cited files. |
| Dependency Graph | Dependency graph, read selected files. |
| Settings | Profile, logout, future API key and provider connection management. |
| Billing | Future billing APIs; no billing endpoint is defined in the MVP API spec yet. |
| Admin Dashboard | Future admin APIs; current MVP API spec does not expose admin management endpoints yet. |

Alignment rules:

- UI must not display workflows that imply unsupported backend capabilities without labeling them as future or disabled.
- Repository Chat must render `citations` from chat responses rather than a separate source-reference concept.
- Indexing UI must poll `indexing_jobs` through the index status endpoint.
- File Explorer must use `repository_files` and `code_chunks` through the file, search, and explain endpoints.
- Blaming users for provider, indexing, or permission problems.
