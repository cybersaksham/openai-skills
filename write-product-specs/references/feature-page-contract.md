# Feature page contract

## Contents

1. Feature boundary
2. Required reading order
3. Product sections
4. System-design sections
5. Low-level architecture sections
6. Cross-layer consistency
7. Detail calibration

## 1. Feature boundary

Create one page for one coherent capability recognized by a user or operator. The page owns its complete
experience and implementation shape across all participating runtimes.

Do not create separate feature pages merely for:

- interaction surface versus authoritative runtime;
- interface versus workflow;
- AI versus non-AI phases of the same capability;
- reporting intrinsic to the feature;
- visual design intrinsic to the feature;
- an internal model or service with no independent user outcome.

Create a separate page when the capability has a distinct user goal, lifecycle, authority boundary, or can be
planned and shipped independently without becoming an incomplete layer of another feature.

## 2. Required reading order

Order the page so a human can stop before code-level detail while an implementer can continue:

1. Purpose, goals, non-goals, and people
2. Success signals and dependencies
3. End-to-end flows, screens or surfaces, and every meaningful state
4. Conceptual model, permissions, and product rules
5. Edge cases, acceptance behavior, and future boundaries
6. High-level system design
7. Low-level code architecture and exact reference contracts

Complete product behavior always precedes system and code architecture. Do not move edge cases, acceptance,
or future boundaries below implementation detail merely because those sections also drive tests and extension
seams.

Use page anchors consistently. The default section ids are listed below; preserve stable ids once published.

## 3. Product sections

### `why`

Explain the user/business problem, present harm, and value created. Do not repeat the feature name as a
definition.

### `goals` and `non-goals`

State measurable outcomes and explicit exclusions. Non-goals prevent implementers from adding plausible but
unapproved behavior.

### `people`

For every actor, state their motivation, authority, and relationship to the flow. Include system/operator
personas when they perform meaningful work.

### `success`

Define product signals and guardrails. Separate outcome metrics from operational health. Avoid invented
numeric targets; mark owner decisions when a target is required but absent.

### `dependencies`

List prerequisite capabilities, shared primitives, external systems, and policies. Say whether each is a hard
runtime dependency, optional enhancement, or future seam.

### `flows`

Document every end-to-end flow, not only the happy path. Each flow identifies:

- initiating actor and entry condition;
- ordered user and system steps;
- authoritative state changes;
- success terminal state;
- interruption, retry, denial, cancellation, expiry, or recovery paths;
- downstream notifications, jobs, analytics, or cross-feature effects.

### `screens`

List every screen/surface and its actor. Define information hierarchy, actions, validation, permissions, and
all meaningful states: loading, empty, ready, editing, pending, success, partial success, error, forbidden,
stale, retry, offline/reconnecting, and terminal states as applicable. Include responsive and accessibility
behavior.

### `states`

Name the stable product and interaction states used across flows and surfaces. Define what each state means,
which actor can observe it, and how it begins, ends, expires, or recovers. Keep this vocabulary identical to
transition, interface, persistence, and test contracts.

### `conceptual-model`

Explain the user-visible concepts, ownership, relationships, and lifecycle without assuming a storage
technology. This product model must reconcile with exact persisted or external records later in the page.

### `rules`

Capture product invariants in plain language. Rules must agree with database constraints, services, state
transitions, interface errors, and UI copy later in the page.

### `permissions`

For each action/read, state actor, scope, object relationship, freshness of authority, denial semantics, and
audit requirement. UI visibility is never the only enforcement.

### `edge-cases`

Cover missing prerequisites, duplicates, concurrency, stale data, retries, out-of-order messages, partial
external failure, revocation, archival/deletion, time boundaries, malformed evidence, large volume, and
platform limitations when relevant.

### `acceptance`

Write externally meaningful behavior that can be proven. Include negative, permission, recovery, and
historical-integrity clauses, not only successful creation.

### `future`

State extension seams and deferred behavior. Clearly distinguish designed compatibility from promised scope.

## 4. System-design sections

### `system-design`

Summarize domain ownership, participating runtimes, source of truth, synchronous/asynchronous boundaries, and
external ownership. Explain why the partition fits the product invariants. If the real topology combines or
omits conventional layers, document that boundary directly instead of manufacturing an artificial layer.

### `runtime-flow` / runtime execution flow

For each command or asynchronous effect, map entrypoint to policy, service, transaction, persistence, outbox,
adapter/job, and terminal state. Use the actual architecture's vocabulary rather than forcing a server model.

### `interaction-flow` / interaction execution flow

For each surface, map its entrypoint to data load, local/remote state owner, input/controller, command,
cache or state reconciliation, transition/navigation, error, interruption, and reconnect behavior. A surface
may be visual, conversational, programmatic, physical, or operator-facing.

### `commands`

Catalog command, actor, guards, transaction owner, writes, emitted effects, idempotency, and failures.

### `queries`

Catalog query, visibility scope, filters/sort/page, returned projection, sensitive-field handling, freshness,
and performance expectations.

### `transitions`

Use a table:

| Aggregate | From | Trigger/guard | To | Side effects/invariants |
| --- | --- | --- | --- | --- |

Include illegal and racing transitions through stable failures or tests.

### `contracts`

Define cross-feature and external boundaries with exact input/output meaning and ownership. Consumers may not
read another feature's private tables/state to bypass the contract.

### `reconciliations`

Record ambiguous, conflicting, superseded, or excluded statements and their current meaning. Link material
choices to decision ids.

### `tests`

List feature-specific verification obligations across domain, persistence, interface, client, end-to-end,
security, concurrency, reliability, migration, and provider-contract layers.

## 5. Low-level architecture sections

### `implementation-manifest`

Provide the intended folder/file/module map for all participating runtimes. Every row states the owned
responsibility. Include shared/generated files only when this feature owns or consumes them.

### `runtime-files` / runtime files

Name exact paths or package/module identities after repository architecture is decided. Split model, command,
read, policy, transport, job, adapter, admin/operator, telemetry, and test responsibilities where applicable.

### `storage-schema` / persisted records

For every record define:

- table/collection/stream and code model identity;
- fields with types, lengths/precision, defaults, nullability, enum values;
- primary, foreign, unique, check, and exclusion constraints;
- deletion, archival, versioning, and historical behavior;
- indexes and query they support;
- tenant/owner keys and cross-boundary invariant.

Use the equivalent exactness for non-relational, event-sourced, local, vector, graph, or file-backed storage.

### `command-contracts`

Give typed signatures or language-appropriate contracts. State authorization, validation, locking,
transaction boundary, idempotency, writes, emitted effects, provider-call timing, and stable error codes.

### `query-contracts`

Give typed read signatures. State scope construction, filters, projection/DTO, pagination/order, sensitive
redaction, cache/freshness behavior, and query-count/performance expectations.

### `interface-contracts`

For each HTTP/RPC/message/CLI/device operation define method/topic, path/name, authentication, input, success,
failure, concurrency/idempotency, pagination, and authorization-hiding behavior. Include exact stable schemas
or a normative schema location.

### `interaction-manifest` / interaction module manifest

List exact surface and interaction-module files, generated schemas or adapters, query identities, inputs,
controllers, components or presenters, state machines, accessibility/adaptation behaviors, and test files.
Define ownership according to the actual topology rather than assuming a browser or separate client.

### `integration-contracts`

For every external system define ownership boundary, adapter operation, credential and configuration scope,
protocol/version, inbound verification, idempotency, timeout, retry/backoff, rate limit, degraded behavior,
reconciliation, test environment, privacy, observability, and operator recovery. State explicitly when the
feature has no external integration or when integration work is excluded from current scope.

### `job-contracts`

For every job/consumer/schedule define signature, trigger, input identifier, idempotency key, authority recheck,
retry/backoff, external effects, terminal failure/dead-letter behavior, observability, and replay rules.

### `migration-contracts`

Define initial or incremental schema order, backfills, compatibility window, deployment/rollout dependency,
rollback or forward-fix behavior, and proof queries/tests. If the feature persists no state, state that and
identify the actual state owner.

### `operations-contracts`

Define environment differences, required configuration and startup validation, secret ownership, release and
rollout gates, rollback or forward-fix policy, backup/restore needs, disaster recovery, scaling limits,
service-level signals, alerts, runbooks, replay/repair tools, and operational ownership. State explicitly when
the owner excludes deployment or operations from the specification scope; silence is not an exclusion.

### `telemetry-contracts`

Name feature-specific metrics, structured events/logs, traces, audit signals, attributes, cardinality and
redaction rules, service-level thresholds, alert ownership, and the operational response each signal enables.

### `error-codes`

List stable machine-readable failures. Map each to layer/status, user meaning, retryability, field/action, log
severity, and any intentionally generic response required for security.

## 6. Cross-layer consistency

Audit these equalities:

- Product rules = state-transition guards = service behavior = interface failures = UI allowed actions.
- Surface identities = route/surface manifest = transitions or navigation = interaction module files.
- Conceptual model = exact persisted records = command/query contracts.
- Permission matrix = query scoping = command checks = signed-resource access = tests.
- Event names/payloads = producer writes = consumer contracts = job tests.
- Error vocabulary = runtime declarations = interface schema = interaction rendering = tests.
- Retention/privacy rules = storage fields = cleanup jobs = access paths = logs/telemetry.
- Acceptance clauses = automated evidence and intended implementation files.

Never use one layer to paper over an omission in another.

## 7. Detail calibration

Specify decisions, not code bodies. Include enough pseudo-structure to prevent divergent implementations, but
do not paste full classes, components, migrations, queries, or algorithms unless an algorithm's exact steps
are themselves the product/system contract.

Increase detail when:

- money, permissions, privacy, security, scoring, irreversible state, or external effects are involved;
- concurrency, idempotency, expiry, resume, or partial failure changes outcomes;
- multiple features share a record or contract;
- the same concept can reasonably be modeled in incompatible ways;
- an implementation agent could make a user-visible or migration-heavy choice.

Reduce detail when it is a local refactorable mechanism with no contract, ownership, security, performance, or
historical consequence.
