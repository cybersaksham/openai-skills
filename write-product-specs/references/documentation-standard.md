# Specification documentation standard

Use this standard for every generated `.specs/` site. Adapt terminology, facts, and page inventory to the actual product. Preserve the bundled Stride documentation format exactly. The shell, hierarchy, design tokens, renderer classes, responsive behavior, and documenting patterns are fixed output contracts rather than a style suggestion.

## Contents

- [Reader outcome](#reader-outcome)
- [Information architecture](#information-architecture)
- [Source-backed page inventory](#source-backed-page-inventory)
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

## Source-backed page inventory

Populate `.specs/_inventory.py` before finalizing the page tree:

- `PRODUCT_JOURNEY_INVENTORY` contains every independently understandable actor/system journey.
- `FEATURE_INVENTORY` contains every product capability and links it to journeys, system flows, runtime owners, and scenarios.
- `ARCHITECTURE_FLOW_INVENTORY` contains every independently triggered sequence with its own ordering, persistence, provider, failure, or recovery boundary.
- `RUNTIME_MODULE_INVENTORY` contains settings/common owners and every natural backend application, package, service, bounded context, worker, or equivalent implementation unit, its exact owned paths, public boundary, and complete entry-flow ids.
- `CLIENT_SURFACE_INVENTORY` contains every client/runtime surface, or one concrete reason that client surfaces are not applicable.

Configure `RUNTIME_DISCOVERY_ROOTS` for the repository's real service/app/package roots. The validator enumerates each root's direct source units by extension. Every included unit must map one-to-one through `RUNTIME_MODULE_INVENTORY[].source_unit` to one focused handbook; every exclusion requires a concrete non-runtime reason. Use `mode="root"` only for direct source files in a genuinely single-unit directory. If that directory also contains source-bearing child packages, configure `child-directories` for the same path so those packages remain separate, or choose narrower roots. The validator rejects an unpaired broad root.

Every focused page must resolve to exactly one inventory entry and every entry to its own unique page route. Two source units may not point at the same handbook. Do not combine unrelated packages or services into a broad runtime page merely because they participate in one product journey. Runtime entries use role `settings`, `common`, or `implementation`; list settings first and common foundations second, or give a concrete not-applicable reason of at least twenty characters that identifies where either absent responsibility lives.

## Navigation and shell

Every generated static HTML site must use the bundled shell and frozen assets. It must provide:

- one persistent left sidebar with the root groups `Start here`, `Product journeys`, `Product guides`, `Architecture`, and `Project reference` in that order;
- the Stride-style brand block, specification version, collapsible group/subgroup/feature hierarchy, nav captions, active state, and sidebar footer;
- clear active-page state using `aria-current="page"`;
- collapsible sidebar groups for large documentation sets;
- a focused article column with readable line length;
- breadcrumbs above the article;
- a right-side on-page contents rail generated from stable headings;
- related pages plus previous/next navigation;
- a responsive navigation drawer on narrow screens;
- semantic landmarks, keyboard operation, visible focus, and text labels;
- light/dark theme support using shared local tokens, with exactly one switcher in the top-right bar and no sidebar theme control;
- print rules that remove chrome and preserve content;
- local CSS, JavaScript, and vector assets with no external runtime dependency.

Preserve these one-per-page shell landmarks and their bundled class names: `site-shell`, `navigation-scrim`, `sidebar`, `sidebar-header`, `documentation-nav`, `sidebar-footer`, `main`, `topbar`, `topbar-actions`, `documentation-layout`, `content`, `breadcrumbs`, `page-navigation`, `page-rail`, and `footer`. Preserve the canonical CSS and JavaScript byte-for-byte unless this skill itself deliberately versions the format and updates its asset hashes and conformance tests.

Do not add:

- subtabs or feature-tab strips as a second navigation system;
- a filter/search input that hides navigation or page content;
- page-local navigation competing with the sidebar;
- framework branding or inconsistent visual shells;
- product-specific themes, documentation frameworks, layout rewrites, or page-local visual systems;
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

Place a settings/configuration page first, shared/common platform foundations second, and one implementation-unit page per repository-discovered source unit after them. Use this order on every implementation-unit page:

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
4. Ordered steps whose `symbols` field names exact files/modules/functions/classes/handlers through validation, policy/query, command/domain, worker, and adapter layers as applicable
5. Every step's exact records read and records written, or an explicit reason that the step intentionally performs no read/write
6. Transaction/consistency boundary, lock/order rule, audit/outbox write, and commit point
7. Exact event, queue task, provider, or downstream handoff and what its consumer executes
8. Terminal response, state, and product-visible outcome
9. Duplicate, stale, concurrent, denial, transient, terminal-failure, and operator-recovery behavior

Follow asynchronous and cross-module paths to the terminal product outcome. “Emit event,” “enqueue job,” “call service,” “invoke provider,” “persist,” and “update record” are incomplete without exact symbols, records, owner, contract, mutation, terminal consumer, and recovery.

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
- Shell spacing, typography, colors, cards, tables, code, callouts, rails, and responsive layout match the bundled Stride format.
- Active page and group are obvious.
- No filter input or subtabs exist.
- Breadcrumbs, title, contents rail, related links, and page turns agree.
- Heading order is semantic and anchor links land correctly.
- Wide tables scroll without clipping the document.
- Code, callouts, badges, and tables remain legible in light/dark themes.
- The only theme switcher is visible and operable at the top right.
- Focus is visible and controls have accessible names.
- Mobile navigation opens/closes reliably and does not trap content.
- Long pages remain scannable without turning every paragraph into a card.
- Print output removes chrome and preserves contracts.
- No local filesystem paths, template markers, broken links, or raw markup leak into output.

A screenshot proves presentation only; it does not prove contract completeness.
