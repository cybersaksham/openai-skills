# Specification documentation standard

Use this standard for every generated `.specs/` site. Adapt terminology and page inventory to the actual product; preserve the information architecture, flow-first structure, and professional documentation shell.

## Contents

- [Reader outcome](#reader-outcome)
- [Information architecture](#information-architecture)
- [Navigation and shell](#navigation-and-shell)
- [Page classes](#page-classes)
- [Contract expression](#contract-expression)
- [Schema presentation](#schema-presentation)
- [Executable acceptance presentation](#executable-acceptance-presentation)
- [Single-source ownership](#single-source-ownership)
- [Visual audit checklist](#visual-audit-checklist)

## Reader outcome

A human must be able to understand the complete product, user journeys, data movement, code architecture, failure behavior, and operations without opening application code. An implementation agent must be able to find every relevant decision without inventing behavior or system design.

Every focused page answers one clear question. Its sidebar label and `h1` must tell a reader exactly which journey, runtime sequence, subsystem, module, or contract it explains.

Prefer concrete titles:

- Upload intent, direct transfer, completion, and scanning
- Notification event to in-app and email delivery
- Payment callback verification and order reconciliation
- Workspace invitation to accepted membership
- PostgreSQL bootstrap and rolling migration

Avoid vague titles such as “Backend architecture,” “Integrations,” “Other flows,” “Technical details,” or “Feature behavior” except on explicit routing/catalog pages.

## Information architecture

Preserve these layers while adapting the actual page names:

1. **Home** — product promise, specification authority, scope, and reader routes.
2. **Start here** — reading order, vocabulary, actors, system map, and implementation sequence.
3. **Product documentation** — focused journeys, feature outcomes, states, alternatives, denials, recovery, permissions, and acceptance.
4. **Architecture documentation** — focused runtime flows, module/service handbooks, data, interfaces, auth/scope, uploads/files, notifications, events/jobs, providers, client runtime, migrations, deployment, security, and assurance.
5. **Reference and evidence** — schemas, operations, routes, errors, events/jobs, decisions, requirement coverage, stable scenarios, and conformance.

Overview and catalog pages summarize and route. Focused pages own executable detail. Link in both directions.

## Navigation and shell

The generated static HTML site must provide:

- one persistent left sidebar containing the complete hierarchy;
- clear active-page state using `aria-current="page"`;
- collapsible sidebar groups for large documentation sets;
- a focused article column with readable line length;
- breadcrumbs above the article;
- a right-side on-page contents rail generated from stable headings;
- related pages plus previous/next navigation;
- a responsive navigation drawer on narrow screens;
- semantic landmarks, keyboard operation, visible focus, and text labels;
- light/dark theme support using shared local tokens;
- print rules that remove chrome and preserve content;
- local CSS, JavaScript, and vector assets with no external runtime dependency.

Do not add:

- subtabs or feature-tab strips as a second navigation system;
- a filter/search input that hides navigation or page content;
- page-local navigation competing with the sidebar;
- framework branding or inconsistent visual shells;
- decorative layouts that reduce information density.

When navigation grows, improve page titles, hierarchy, grouping, and progressive disclosure in the sidebar.

## Page classes

### Home and overview pages

State purpose, authority, current scope, non-goals, principal actors, product/system map, and links to focused owners. Overviews never become a second normative copy of detailed contracts.

### Product journey page

Use this order when applicable:

1. Outcome, scope, and non-goals
2. Actors and authority
3. Preconditions
4. Entry points
5. Ordered happy path
6. Alternative, denial, empty, stale, and offline paths
7. State model and durable effects
8. Cross-feature and external handoffs
9. Notifications and audit
10. Failure, retry, cancellation, and recovery
11. Client nonvisual behavior and accessibility
12. Stable acceptance scenarios
13. Related system designs and exact contracts

Describe observable behavior before implementation structure, then link each step to its owner.

### Architecture flow page

Use a dedicated page whenever a subsystem has an independent trigger, ordering, persistence boundary, provider boundary, failure policy, or recovery loop.

Use this order:

1. Purpose, scope, and non-goals
2. Components and ownership
3. Trigger and exact inputs
4. Chronological sequence
5. Transaction, consistency, and lock boundaries
6. Data read/written at each durable point
7. Interface/event/job/provider contracts
8. Idempotency, ordering, duplicates, and concurrency
9. Timeouts, retries, circuit behavior, dead letter, and reconciliation
10. Permissions, secrets, sensitive data, and audit
11. Observability and operator recovery
12. Acceptance and failure-injection scenarios
13. Product journeys that depend on the design

State exactly when external I/O occurs relative to transactions or locks.

### Backend/runtime module handbook

Use the system's natural implementation boundary: application, service, module, package, bounded context, function, worker, or equivalent. Do not force Django terminology or a monolith/microservice topology.

Use this order:

1. Module responsibility, public boundary, dependencies, and owned paths
2. Developer code-flow directory
3. Complete code-format domain/persistence schemas
4. Cross-module product journeys and runtime handoffs
5. Exact service, selector/query, API, event, job, permission, error, transition, and scenario catalogs
6. Canonical owners and related system designs

Every material entry path must have a chronological developer flow before the catalogs. Material paths include state-changing commands, scoped reads, event/message consumers, scheduled work, provider calls/callbacks, and reconciliation/recovery.

Each developer code flow includes:

1. Concrete outcome title and stable id
2. Trigger, initiator, and authority source
3. Exact transport/event/schedule/public entry point
4. Ordered file/module and symbol path through validation, policy/query, command/domain, worker, and adapter layers as applicable
5. Every entity/record/model read, locked, created, updated, or intentionally not written
6. Transaction/consistency boundary, lock/order rule, audit/outbox write, and commit point
7. Exact event, queue task, provider, or downstream handoff and what its consumer executes
8. Terminal response, state, and product-visible outcome
9. Duplicate, stale, concurrent, denial, transient, terminal-failure, and operator-recovery behavior

Follow asynchronous and cross-module paths to the terminal product outcome. “Emit event,” “enqueue job,” “call service,” and “update record” are incomplete without exact owner, contract, mutation, and recovery.

### Frontend/client runtime page

Document routes/screens, composition boundaries, server/cache state, URL state, form/draft state, local visual state, generated-client contract, permission/action authority, loading/empty/denial/error/reconnect/stale/schema-mismatch states, accessibility semantics, analytics/privacy, and test ownership. Adapt this to web, mobile, desktop, CLI, embedded, or API-only clients.

### Contract/reference page

Use structured schemas and tables whose rows are independently interpretable. Every reference row links to the flow or module that owns its behavior.

## Contract expression

Use:

- code blocks for relational/document/domain schemas and sealed public payloads;
- tables for operations, states, transitions, permissions, errors, compatibility, and comparison matrices;
- ordered lists or sequence blocks for chronological flows;
- stable ids for requirements, decisions, flows, operations, states, transitions, events, jobs, provider outcomes, and scenarios;
- short prose for rationale and boundaries;
- diagrams only when they clarify relationships that prose or a small table cannot.

Do not use “standard behavior,” “as above,” “normal errors,” “etc.,” inferred serializer/model fields, open `object`, or ellipses where an agent needs an exact contract.

## Schema presentation

- Keep data schemas in code format, never model-field tables.
- Use the implementation stack's exact native types when known. If a DSL is used, publish deterministic resolution rules.
- Include type/bounds/precision, required/null/blank behavior, defaults, identity, relationships and deletion behavior, uniqueness, checks, indexes, state constraints, history/versioning, retention, and concurrency.
- Keep request, response, event, job, and provider payload schemas sealed. Explicitly define unknown-key and unknown-enum/state behavior.
- Link focused flows to canonical schema blocks instead of copying field lists.

## Executable acceptance presentation

Every stable scenario must expose:

1. Scenario id
2. Actor and exact authority/grants
3. Deterministic fixture and precise pre-state
4. Invocation and parameterized cases
5. Observable response, durable effects, and forbidden effects
6. Time, concurrency, provider, and cleanup controls
7. Required unit/integration/contract/end-to-end/conformance evidence

Avoid placeholder actors, unnamed pre-states, generic outcomes, or tests that merely assert success.

## Single-source ownership

Assign one source module and one focused generated page as the normative owner of each fact. Summaries link instead of independently restating details.

When moving content:

- preserve stable anchors when meaning remains;
- update every inbound reference and navigation entry;
- provide a compatibility route when readers, plans, or agents may hold an old URL;
- update validators and conformance ownership;
- keep historical appendices visibly non-normative.

## Visual audit checklist

Inspect representative home, journey, architecture flow, module handbook, schema/reference, and acceptance pages on desktop and narrow viewports.

- Sidebar hierarchy is understandable without opening pages.
- Active page and group are obvious.
- No filter input or subtabs exist.
- Breadcrumbs, title, contents rail, related links, and page turns agree.
- Heading order is semantic and anchor links land correctly.
- Wide tables scroll without clipping the document.
- Code, callouts, badges, and tables remain legible in light/dark themes.
- Focus is visible and controls have accessible names.
- Mobile navigation opens/closes reliably and does not trap content.
- Long pages remain scannable without turning every paragraph into a card.
- Print output removes chrome and preserves contracts.
- No local filesystem paths, template markers, broken links, or raw markup leak into output.

A screenshot proves presentation only; it does not prove contract completeness.
