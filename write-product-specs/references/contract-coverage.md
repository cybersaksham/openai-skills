# Contract coverage standard

Apply this checklist to every in-scope product journey and system flow. Silence is ambiguity. Mark a dimension `not applicable` only with a reason tied to the product and architecture.

## Contents

- [Product and policy](#product-and-policy)
- [Domain and data](#domain-and-data)
- [Runtime ownership and developer flow](#runtime-ownership-and-developer-flow)
- [APIs, interfaces, and generated clients](#apis-interfaces-and-generated-clients)
- [Events, queues, jobs, and schedules](#events-queues-jobs-and-schedules)
- [Providers and external systems](#providers-and-external-systems)
- [Files, media, and uploads](#files-media-and-uploads)
- [Authorization, security, privacy, and abuse](#authorization-security-privacy-and-abuse)
- [Client and interaction runtime](#client-and-interaction-runtime)
- [Bootstrap, migrations, deployment, and operations](#bootstrap-migrations-deployment-and-operations)
- [Acceptance and conformance](#acceptance-and-conformance)

## Product and policy

Define:

- outcome, users, initiating actor/system, observers, administrators, and affected non-users;
- authority source, scope, grants, delegation, revocation, and denial semantics;
- prerequisites, entry points, validation, ordered happy path, and terminal state;
- alternatives, empty states, duplicates, stale/late/concurrent/offline actions, cancellation, partial completion, and recovery;
- non-goals, excluded future behavior, and cross-feature consequences;
- notifications, audit, privacy visibility, and user-facing explanations.

## Domain and data

For every entity/aggregate/document/record define:

- canonical owner and storage identity;
- exact field names, native types, bounds/precision, required/null behavior, defaults, generated values, and mutability;
- relationships, cardinality, deletion behavior, referential integrity, uniqueness, checks, and indexes;
- legal states/transitions, transition owner, invariants, versioning, history, audit, and immutable evidence;
- tenant/partition/shard/scope identity and query boundary;
- creation, update, archival, soft/hard deletion, retention, purge, export, restore, and legal hold;
- transaction/consistency model, lock or compare-and-swap order, race behavior, and idempotency identity;
- migration/backfill, compatibility, and rollback behavior.

Render canonical schemas in code blocks.

## Runtime ownership and developer flow

Inventory every natural implementation unit from verified repository/architecture discovery before writing handbooks. Configure `RUNTIME_DISCOVERY_ROOTS` so final validation enumerates actual source directories/files, and map each resulting unit one-to-one to `RUNTIME_MODULE_INVENTORY[].source_unit`. Document settings/configuration and shared/common foundations separately, then create one focused page per application, service, package, bounded context, worker, or equivalent code owner. Combining separate discovered units into an aggregate page is a mechanical completeness failure even when that page contains a few representative flows.

For every material entry path define:

- exact interface/event/schedule/CLI/provider callback trigger;
- authentication/verification and authority construction;
- input parsing/validation and stable failure mapping;
- exact module/file and symbol sequence at every chronological step;
- query/policy selector and command/domain owner;
- records read and records written at every step, including explicit no-read/no-write reasons where applicable;
- transaction start/commit/rollback, consistency boundary, lock order, audit/outbox write, and post-commit work;
- cross-module public seam and dependency direction;
- event/job/provider/downstream handoff, consumer execution, and terminal outcome;
- duplicate, stale, concurrent, transient, permanent, poison-message, and operator-recovery behavior;
- logs, metrics, traces, alerts, safe attributes, and sensitive-data exclusions.

Catalogs are field/signature lookup aids. They never replace chronological code flows.

Keep `.specs/_inventory.py::RUNTIME_MODULE_INVENTORY[].entry_flows` equal to the complete developer code-flow directory rendered on that unit's page. Keep `source_unit` equal to one included repository-discovered unit and include it in `owned_paths`. A flow present in code discovery but absent from both is a completeness failure; a rendered flow absent from the inventory has no accountable discovery owner.

## APIs, interfaces, and generated clients

For each operation define:

- stable operation id, protocol, method/path/topic/command, version, authentication, and scope/tenant context;
- path/query/header/cookie/body schema with required/default/unknown-field behavior;
- exact sealed success DTO/payload and all statuses/outcomes;
- stable error codes, field-error shape, retryability, and information-disclosure behavior;
- pagination/cursor/order/filter/search semantics and consistency window;
- idempotency/precondition/version headers and duplicate/conflict responses;
- rate/size/time limits, caching, conditional requests, and streaming behavior;
- generated client name, native types, compatibility, and unknown-enum/state fallback;
- deprecation, versioning, backward/forward compatibility, and rollout sequence.

Do not use a framework serializer, ORM model, GraphQL resolver, protobuf generator, or client convenience type as the unstated public contract.

## Events, queues, jobs, and schedules

For every asynchronous contract define:

- stable name, version, producer, trigger, publication/dispatch point, and payload schema;
- partition/routing key, ordering scope, delivery guarantee, deduplication identity, and retention;
- consumer owner, exact handler, authority/scope propagation, and data effects;
- retry classification, delays/backoff/jitter, maximum attempts/age, timeout, and cancellation;
- dead-letter/failed-job location, replay authorization, replay safety, poison handling, and reconciliation;
- observability, alert thresholds, correlation ids, and sensitive-data policy;
- deployment compatibility between producer and consumers.

## Providers and external systems

Define:

- adapter/anti-corruption boundary and provider-specific implementation;
- credential owner, scope, storage, rotation, and redaction;
- normalized command/input and normalized outcome/error taxonomy;
- timeout, retry, rate limit, circuit/bulkhead, fallback, and cost/quota behavior;
- webhook/callback signature, timestamp/freshness, replay protection, deduplication, and out-of-order handling;
- reconciliation source of truth, schedule, mismatch resolution, operator controls, and audit;
- sandbox/fake behavior and deterministic tests;
- data residency, privacy, retention, deletion, and provider termination/export.

## Files, media, and uploads

If applicable define:

- intent creation, ownership, file constraints, content type/sniffing, checksum, direct/proxied transfer, multipart behavior, and expiry;
- quarantine, scanning/transcoding/processing, completion verification, deduplication, and failed/abandoned cleanup;
- metadata and blob state synchronization;
- public/private access classes, authorization timing, signed URL/cookie lifetime, cache policy, revocation, and deletion;
- provider callback/event ordering, retries, reconciliation, and operator recovery;
- download/export audit and sensitive-content handling.

Do not summarize all asset classes under one access policy when their disclosure or lifetime differs.

## Authorization, security, privacy, and abuse

Define:

- identity/session/token lifecycle, authority source, roles/capabilities, row/object scope, hierarchy, and policy owner;
- scope application before count/aggregation/pagination/serialization;
- absent versus forbidden versus invalid denial behavior;
- privilege escalation boundaries, administrative override, break-glass, and audit;
- input validation, output encoding, request forgery/injection protections, signature verification, and secret handling;
- sensitive/personal data classification, collection purpose, minimization, encryption, logging/telemetry exclusions, retention, export, deletion, and consent;
- rate limits, quotas, spam/fraud/abuse controls, suspension, appeal, and operator tools;
- threat/failure cases and executable security evidence.

## Client and interaction runtime

Define:

- route/screen/surface inventory and composition owner;
- server/cache state, URL/navigation state, form/draft state, attempt/workflow controller state, and local visual state;
- authoritative DTO/action/permission source and stale-grant behavior;
- loading, empty, denial, validation, recoverable/permanent error, optimistic update, stale, reconnect, offline, and schema-mismatch behavior;
- back/refresh/deep-link/multi-tab or multi-device behavior where applicable;
- semantic structure, keyboard, focus, labels, announcements, contrast/non-color cues, motion, and responsive behavior;
- analytics/telemetry event and privacy rules;
- component/unit/integration/end-to-end and accessibility evidence.

If page-level visual design is not approved, keep visual delivery readiness explicitly deferred while fully specifying nonvisual behavior.

## Bootstrap, migrations, deployment, and operations

Define exact executable values and owners for:

- local/fresh install, environment inventory, required/default configuration, secret injection, and dependency readiness;
- schema/data migration ordering, online compatibility, background backfill, dual-read/write window, validation, resume, and rollback boundary;
- build/artifact generation, deployment order, health/readiness/startup, traffic stages, observation duration, and rollback triggers;
- capacity, scaling, timeouts, queues, caches, scheduled maintenance, and graceful shutdown;
- backup coverage, retention, restore procedure/proof, RPO, RTO, disaster recovery, and regional/provider failure;
- dashboards, alerts, runbooks, reconciliation, repair commands, access controls, and audit;
- feature flag/config ownership, emergency disablement, and cleanup.

“Configurable,” “supported,” or “defined by operations” is incomplete without the exact owner, value/range, and safe behavior.

## Acceptance and conformance

For every stable scenario record:

- stable scenario id and linked requirements/decisions;
- exact actor, authority, tenant/scope, fixture ids, pre-state, clock, idempotency/version keys, and provider fake;
- command/invocation and parameter cases;
- response/status/error and client-visible result;
- exact durable writes, state transitions, events/jobs/provider calls, audit/telemetry, and forbidden side effects;
- concurrency/barrier/failure injection/retry controls and cleanup;
- expected unit, repository/database, service, API/contract, consumer/provider, client, end-to-end, security, migration, and conformance evidence.

Map each normative clause to its implementation target and test/evidence location during planning and final reconciliation.
