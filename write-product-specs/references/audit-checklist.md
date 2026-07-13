# Specification audit checklist

## Contents

1. Audit order
2. Requirement coverage
3. Decision completeness
4. Product and UX completeness
5. Architecture completeness
6. Cross-page consistency
7. Implementation simulation
8. Mechanical and visual validation
9. Definition of final

## 1. Audit order

Audit in this order because later checks depend on earlier authority:

1. Input and requirement coverage
2. Confirmed decisions and reconciliations
3. Feature behavior and end-to-end flows
4. Cross-cutting architecture
5. Low-level code architecture
6. Cross-page identity/contract parity
7. Implementation simulation
8. Mechanical and visual quality

Fix source modules, regenerate, and restart affected downstream checks after each material correction.

## 2. Requirement coverage

- Every meaningful supplied clause has one stable requirement id.
- Every requirement retains a useful source reference without making that source necessary to understand the
  rendered specification.
- Compound statements are split when their parts can have different destinations or status.
- Every non-superseded requirement maps to one or more rendered page anchors.
- Every mapped destination exists and actually contains the behavior, not only a keyword.
- Exclusions and non-goals are mapped as carefully as positive behavior.
- Later owner corrections supersede stale rows explicitly.
- No requirement exists only in a historical appendix, comment, chat transcript, or hidden generator field.
- Summary pages do not contradict the more exact feature/system sections.

Perform a reverse audit too: each major documented behavior should have a requirement, decision, or explicitly
derived architecture rationale so accidental invention is visible.

## 3. Decision completeness

Search for language that hides uncertainty: “may,” “could,” “probably,” “as needed,” “TBD,” “appropriate,”
“standard,” “etc.,” “later,” or multiple alternatives joined by “or.” Determine whether each is intentional
flexibility or a missing choice.

For every material decision verify:

- owner confirmation and its context are recorded;
- the chosen behavior is stated positively;
- consequences are applied to every feature and contract;
- rejected/superseded behavior no longer appears as current truth;
- future possibilities remain clearly non-current;
- no implementation agent must choose a product policy, data owner, interface meaning, permission model,
  security boundary, or irreversible migration shape.

Final specs have no unresolved material decision. If the owner has not answered, report the exact blocker
instead of marking the documentation complete.

For a rough cut awaiting answers, verify that every unaffected area is fully authored and that validation
fails on explicit pending decision/requirement rows, not generic scaffold placeholders.
The generator should still render an incomplete feature with a visible gap callout; missing design manifests
must not turn the build into a traceback.
The exact unresolved status literal is `pending`; `pending while drafting` is explanatory prose, never a stored
value. Final documentation contains no `pending` requirement or decision row.

## 4. Product and UX completeness

For each actor and feature verify:

- the problem and goal are understandable without technical context;
- entry points, prerequisites, happy path, alternate path, cancellation, denial, recovery, and terminal state
  are present;
- all screens/surfaces and all meaningful UI states are documented;
- validation and error copy meaning match authoritative runtime failures;
- navigation/deep-link/back/refresh/reconnect behavior is defined when relevant;
- accessibility, responsive/device constraints, keyboard/focus, and destructive confirmation are covered;
- notifications, analytics, audit, exports, approvals, or operator work triggered by the flow are included;
- history, versioning, archival, deletion, and revoked-access behavior are visible to the user correctly;
- goals, non-goals, success signals, and future seams do not conflict.

Trace at least one golden and one failure journey per actor through every participating layer.

## 5. Architecture completeness

### Repository and ownership

- Every intended repository/root/package has a purpose.
- Dependency direction and forbidden imports/calls are explicit.
- Shared primitives have one owner and feature-specific behavior remains with the feature.
- Generated artifacts and their source are named.
- Local, test, and required configuration contracts are defined without placing secrets in documentation.

### Data

- Conceptual aggregates align with exact persisted records.
- Every record has keys, types, nullability/defaults, relationships, constraints, indexes, deletion/history, and
  tenant/owner rules.
- Cross-record invariants name the transaction/lock owner.
- Immutable/versioned/superseding semantics are unambiguous.
- Migration/backfill and compatibility behavior exists for risky schema changes.
- Feature-specific telemetry names signals, safe attributes, thresholds, and the response they drive.

### Commands and reads

- Every mutation has actor, input, guards, transaction, idempotency, writes, effects, output, and stable errors.
- Every read has scope, filters/order/page, projection, redaction, freshness/cache, and performance behavior.
- Provider calls do not occur in an unsafe transaction phase or without retry/idempotency policy.
- Concurrency and duplicate/out-of-order cases have authoritative outcomes.

### Interfaces, events, and jobs

- Exact operations, schemas, authentication, status/failure semantics, and versioning are present.
- Event identity, version, producer, payload, consumers, and privacy are present.
- Job trigger, input id, deduplication, retries, terminal state, replay, and observability are present.
- External ownership, credential/config scope, callback verification, rate/timeout/failure behavior are present.

### Integrations

- Every external system has an owner, purpose, data classification, and authoritative boundary.
- Adapter operations, protocol/version, request/response or message meanings, and compatibility policy exist.
- Credential and configuration scope, storage owner, access, rotation/revocation, and environment separation are explicit.
- Inbound callbacks define authentication/signature verification, replay defense, idempotency, ordering, and acknowledgement.
- Timeouts, retries/backoff, rate limits, circuit/degraded behavior, duplicate handling, and reconciliation are explicit.
- Sandbox/test doubles, provider contract tests, safe observability, outage handling, and operator recovery exist.

### Security, privacy, and operations

- Identity, session/token, authorization, tenant isolation, and current-grant rechecks are explicit.
- Sensitive fields, encryption, secrets, logs, traces, analytics, exports, and signed access are classified.
- Retention/deletion and audit requirements have executable owners.
- Abuse/rate limiting, file/input validation, injection/content safety, and webhook forgery are covered.
- Metrics, structured logs, traces, alerts, run/replay tools, and performance budgets target user outcomes.
- Every environment names its purpose, topology differences, data policy, required configuration, and promotion boundary.
- Required configuration fails fast; defaults, validation, owner, and secret versus non-secret classification are explicit.
- Release prerequisites, migration order, rollout gates, compatibility window, verification, rollback or forward-fix are explicit.
- Backup/restore scope, recovery objectives when required, disaster scenarios, restore drills, and recovery authority are explicit.
- Capacity assumptions, scaling boundaries, service-level indicators/objectives, alert thresholds, escalation, and runbooks exist.
- Operational ownership covers incidents, replay/repair, scheduled maintenance, provider outages, and audit evidence.

## 6. Cross-page consistency

Build and mechanically compare identity sets where applicable:

- feature slugs across manifest, feature data, system design, low-level design, routes, events, and generated pages;
- model/table names across domain model, data dictionary, feature schema, service signatures, and events;
- routes/operations across surface catalog, interaction manifest, interface reference, and generated schema;
- event names across feature events, event catalog, producer and consumer/job lists;
- states across product flow, transition table, DTO/schema, screen states, errors, and tests;
- permissions across matrix, selectors, services, signed resources, UI actions, and denial tests;
- configuration names across repository/env docs and runtime owners;
- decision consequences across every affected page;
- decision-register entries render the affected features, pages, and contracts instead of keeping that
  relationship only in authored source.

Search generated curated content for superseded phrases after each correction. Add validator assertions for
high-risk regressions.

## 7. Implementation simulation

Perform a cold-read simulation for each feature. Assume the implementer has only `.specs/` and ask:

1. Where does this code live and what may it depend on?
2. Which record owns truth and what exact fields/constraints/history does it have?
3. Which command starts each flow and who may invoke it?
4. What locks, transaction, idempotency, and external-effect order are required?
5. Which query feeds each screen and how is access scoped?
6. What exact interface, event, or job connects layers?
7. What does every loading, empty, error, retry, interrupted, and terminal state show/do?
8. What happens on duplicate, race, timeout, revocation, deletion, or partial failure?
9. Which tests prove behavior, structure, permissions, and regression safety?
10. Which decision would the implementer still have to make?

Any substantive answer to question 10 is an audit finding. Resolve it in the decision register and affected
specs before finalization.

Also perform the reverse simulation: choose a model, endpoint, event, route, or job from a feature and verify
that its purpose and consumer are evident. Orphan technical elements usually indicate over-design or missing
product documentation.

## 8. Mechanical and visual validation

### Mechanical

- Generator exits successfully from the documented repository root.
- Validator exits successfully with no skipped checks.
- All expected pages exist.
- Relative links, anchors, scripts, stylesheets, and local media resolve.
- Every major `h2` section has a stable id for requirement and decision links.
- Rendered pages contain no unsafe link schemes or required network-hosted assets.
- HTML ids are unique per page.
- Stable identity sets are equal across source modules.
- Requirement destinations resolve.
- No placeholders or unresolved decision markers remain.
- No generated HTML differs after a second build.
- Source and generated files pass repository formatting and diff checks.

### Visual

Inspect at least:

- overview/home;
- system/repository architecture;
- one dense feature page;
- one table-heavy reference page;
- desktop width;
- narrow/mobile width;
- print preview or print stylesheet when the site supports it.

Verify nested navigation, active state, menu behavior, search/filter, heading hierarchy, anchors, cards, tables,
code blocks, long identifiers, overflow, contrast, focus visibility, and empty/pending callouts. Fix layout at
the shared shell/asset level rather than per-page hacks.

## 9. Definition of final

The specification system is final only when all are true:

- Humans can explain the complete product and each actor journey from the rendered documentation.
- Implementation agents can build every in-scope feature without another requirements source or an unrecorded
  product/system-design choice.
- Product behavior and low-level architecture are both present, with no build-ticket tone.
- Requirement, decision, route, model, interface, event, state, permission, and test contracts are internally
  consistent.
- All material owner decisions are resolved and propagated.
- Mechanical validation and representative visual inspection pass.
- Explicit non-goals and future boundaries prevent accidental scope expansion.
- The final report names any true external blocker instead of disguising it as completion.
