# Product specification system

## Contents

1. Documentation principles
2. Canonical folder structure
3. Page taxonomy
4. Navigation and presentation
5. Authored-source model
6. Requirement and decision control
7. Architecture depth
8. Adapting the system

## 1. Documentation principles

### One standalone authority

The generated `.specs/` site is the complete explanation of intended product behavior and system design.
Source notes may help produce it, but readers must not need those notes. Historical context is optional and
must never override curated documentation.

### Product documentation first

Write for two readers at once:

- Humans need purpose, vocabulary, people, journeys, screens, examples, consequences, and boundaries.
- Implementers need ownership, exact records, interfaces, transitions, failures, security, and verification.

Do not make the site resemble a backlog or an engineering handoff. A feature page should read naturally from
why the capability exists through how the complete system represents it.

### Decision-complete, not thought-free

Remove product and system-design ambiguity, not engineering judgment. Implementation agents still reason
about code quality and local mechanics, but they do not choose behavior, ownership, persistence shape,
interface semantics, permission policy, or failure meaning that the specs should define.

### Curated truth over duplication

Define shared primitives once and link to them. Feature pages explain how they specialize the primitive.
Duplicate prose tends to drift; exact mappings and feature-specific exceptions should remain explicit.

## 2. Canonical folder structure

Use this default layout for a substantial software product:

```text
.specs/
├── _build.py                    # deterministic static-site generator
├── _validate.py                 # mechanical and product-specific assertions
├── _manifest.py                 # product metadata and navigation groups
├── _requirements.py             # atomic requirement coverage register
├── _pages.py                    # overview and cross-cutting authored content
├── _features.py                 # product-facing feature definitions
├── _system_design.py            # feature execution, transitions, contracts
├── _low_level_design.py         # files, records, signatures, interfaces, jobs
├── _routes.py                   # route/screen manifest when a UI exists
├── _events.py                   # event and consumer contracts when applicable
├── .gitignore                   # generator caches only
├── assets/
│   ├── styles.css
│   ├── specs.js
│   └── favicon.svg
├── features/                    # generated feature pages
│   └── <feature-slug>.html
├── index.html                   # generated documentation home
└── <cross-cutting-page>.html    # generated reference pages
```

Small products may combine source modules. Large products may split them by domain. Preserve these invariants:

- Authored generator/data files begin with `_`.
- Generated pages are ordinary `.html` files with stable names.
- Feature pages live under `features/`.
- Shared local assets live under `assets/`.
- The site has one root entrypoint: `.specs/index.html`.
- Commit authored sources and generated output together when the repository uses specs as an implementation
  authority, so a reader can open the current documentation without running a generator.
- Cache files and local preview artifacts are ignored.

Never require an application toolchain merely to read the documentation. A standard-library generator and static
HTML keep the source of truth durable and locally openable. The bundled scaffold uses Python 3.10 or newer;
that documentation-tooling baseline is independent of the product's runtime stack.

## 3. Page taxonomy

Use the following page set as a coverage model, then adapt names to the product.

### Product

| Page | Required content |
| --- | --- |
| Overview | Product promise, audience, vocabulary, feature map, current scope, documentation map |
| Experience and flows | Global information architecture and end-to-end actor journeys |
| Decisions | Confirmed choices, rationale, consequences, affected contracts, unresolved gate while drafting |
| Roadmap and boundaries | Current scope, designed extension seams, future possibilities, explicit exclusions |

### Architecture

| Page | Required content |
| --- | --- |
| System overview | System context, runtime/container boundaries, ownership, synchronous/asynchronous flows |
| Repository blueprint | Exact roots, modules/packages, dependency direction, generated artifacts, commands |
| Runtime architecture (`runtime-architecture.html`) | Command lifecycle, ownership boundaries, storage/transactions, asynchronous work, configuration |
| Interaction surfaces (`interaction-surfaces.html`) | Surface inventory, entry and transition rules, interaction modules, state, feedback, accessibility/adaptation |
| Domain model | Aggregates, relationships, lifecycle, history/versioning, cross-domain contracts |
| Data dictionary | Field-level records, types, nullability, keys, constraints, indexes, deletion/retention |
| Permissions | Actors, capabilities, scope rules, object checks, denials, audit requirements |

Add separate shared-kernel or domain-spine pages when three or more features depend on the same exact model or
algorithm. Add native/mobile/device/ML/data-pipeline pages when those are first-class runtimes.

### Features

Create one holistic page per user-recognizable capability. Do not split experience, runtime execution,
automation, reporting, or later phases into separate features when they are intrinsic layers of the same
capability. Use nested feature groups in navigation when the catalog is large.

Follow `feature-page-contract.md` for every feature page.

### Reference

| Page | Required content |
| --- | --- |
| Transport/interfaces | Conventions plus exact operations, inputs, outputs, stable failures, authentication |
| Events and jobs | Event envelopes, producer/consumer catalog, triggers, idempotency, retry, terminal behavior |
| Integrations (`integrations.html`) | System inventory, ownership, capability/adapter contracts, credential scope, inbound verification, timeouts/retries/rates, degradation/reconciliation, test environments, observability |
| Operations (`operations.html`) | Environments, configuration validation, secrets, data changes, rollout, rollback/forward-fix, backup/restore, disaster recovery, capacity, service levels, alerts, runbooks, ownership |
| Quality and security | Test matrix, privacy, retention, threat controls, performance, observability |
| Implementation sequence | Dependency-aware vertical order and proof gates, not estimates or assignments |
| Coverage/audit | Requirement traceability, feature-section completeness, contradiction and readiness status |

The named pages are the default coverage topology, not a required product topology. Split them when multiple
first-class runtimes or surfaces need separate treatment; combine them when one boundary owns several concerns
and clarity improves. Update navigation, renderer, validator, and requirement destinations together. Never
omit a concern because it has no dedicated page, and never invent an artificial layer merely to retain a page.

## 4. Navigation and presentation

Use a responsive documentation shell with:

- a persistent desktop sidebar and mobile menu;
- top-level nested groups such as Product, Architecture, Features, and Reference;
- feature subgroups based on product meaning rather than code package;
- current-page indication and stable relative links;
- page-local text filtering or search;
- semantic headings with stable ids and scroll offsets;
- horizontally scrollable table wrappers;
- print styles that hide navigation and preserve readable content;
- keyboard-operable native controls (`details`, links, buttons, inputs);
- no required network requests, external fonts, or build server.

Use visual components intentionally:

- Hero: purpose and page scope.
- Flow: ordered actor/system journey.
- Cards: parallel concepts or feature catalog.
- Table: exact mappings, contracts, matrices, records, permissions.
- State chips: finite vocabulary.
- Callout: decision, warning, boundary, or important invariant.
- Code block: paths, schemas, example payloads, repository trees.
- Nested disclosure: dense reference detail that should not dominate human narrative.

Avoid decorative dashboards, fake metrics, excessive badges, or visuals that make dense specifications harder
to scan.

## 5. Authored-source model

Generated HTML must be reproducible. Treat source modules as normalized product data and renderer logic:

- `_manifest.py`: metadata, page groups, feature groups, stable slugs.
- `_requirements.py`: one row per atomic input clause with rendered destinations.
- `_pages.py`: curated cross-cutting narrative and tables.
- `_features.py`: purpose, people, flow, screens, rules, acceptance.
- `_system_design.py`: architecture, commands, reads, transitions, cross-feature contracts, reconciliations.
- `_low_level_design.py`: file/package ownership, records, exact signatures, interface operations, jobs,
  migrations, telemetry, and errors.
- `_routes.py`: route, owning file/module, screen contract, required states.
- `_events.py`: event name/version, producer, payload, consumers/effects.

The build should derive repeated tables from these structures rather than maintain copies. The validator should
compare the same identities across modules.

Do not hand-edit an HTML correction. Change its source, rebuild all affected pages, and validate. The build
must remove stale generated pages when a feature or cross-cutting page is deliberately removed.

## 6. Requirement and decision control

### Requirement register

Assign stable ids such as `REQ-001`. Each row contains:

- lossless requirement text;
- source reference such as a prompt clause, discussion, document location, or observed behavior;
- classification: behavior, architecture, constraint, quality, exclusion, or decision;
- owning feature/cross-cutting area;
- one or more `page.html#section` destinations;
- status: `covered`, `superseded`, or `pending`;
- optional notes about conflicts or interpretation.

`pending` is the exact literal used while drafting. Never write `pending while drafting` as a status value.
Finalization requires every non-superseded row to be `covered` and every destination to exist.

Pending owner choices do not suspend documentation work. Fully author all known behavior, record each real gap
as an explicit `pending` requirement or decision row, and state the constrained alternatives only where that
decision changes the result. An incomplete rough cut should fail validation because of those explicit rows,
never because pages or feature manifests were left as starter placeholders. Final documentation contains no
`pending` row.

### Decision register

Assign stable ids such as `DEC-001`. Capture:

- question or ambiguity;
- confirmed choice;
- why it was chosen;
- consequences and rejected alternatives when material;
- affected features/pages/contracts;
- confirmation context identifying where the owner made the choice;
- confirmation state.

Do not invent a material decision to make the register green. Ask the owner. Once confirmed, update every
consumer—not only the decision page.

### Reconciliation register

Each feature page should explain how conflicting, historical, or vague statements resolve into current
behavior. Use statuses such as confirmed, clarified, superseded, excluded, or owner decision required. The
curated feature sections remain authoritative.

## 7. Architecture depth

Code-centric means the documentation fixes the design shape without pasting the implementation. At minimum,
define when applicable:

- runtime and repository boundaries;
- domain ownership and dependency direction;
- conceptual aggregates and exact persisted records;
- identifiers, field types, defaults, nullability, relationships, constraints, indexes, deletion, history;
- command and query signatures, authorization, transaction/lock boundary, idempotency, stable failures;
- interface paths/topics/methods, request and response shapes, concurrency, pagination, errors;
- event/job signatures, triggers, payloads, consumers, retries, deduplication, terminal states;
- interaction-surface and module ownership, state source, loading/empty/error/stale/offline/success states;
- authentication, permission, secret, privacy, retention, audit, observability, and abuse controls;
- migration/backfill and backwards-compatibility strategy;
- unit, integration, contract, end-to-end, security, reliability, and regression obligations.

If the product does not have one of these layers, say why it is not applicable rather than generating a fake
layer.

## 8. Adapting the system

- Match the user's terminology. Create a glossary when terms can be confused.
- Specialize architecture only after the stack and operational shape are decided.
- Use the actual repository layout when code exists; otherwise document the intended layout explicitly.
- Split or combine the default pages and source modules to match actual ownership and execution boundaries; a
  single-runtime product does not need a manufactured interaction or service layer.
- For hardware, data, ML, automation, or integration-heavy products, promote their lifecycle and failure
  contracts to first-class pages.
- Integrations and operations are required coverage unless the owner explicitly excludes them. Otherwise
  document environments, configuration/startup validation, secrets, migrations/data changes, rollout,
  rollback or forward-fix, backup/restore, disaster recovery, capacity, service levels, alerts, runbooks, and
  operational ownership.
- Preserve extension seams for known future phases, but do not specify future behavior as current scope.
