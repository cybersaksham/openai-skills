---
name: maintain-specifications
description: Create, update, restructure, reconcile, audit, rate, or validate this repository's authoritative generated `.specs/` product and architecture documentation. Use automatically for every task that reads or changes specification sources/pages, documentation structure, product flows, runtime module developer code flows, code-format data schemas, sealed interface schemas, ownership, events/jobs, permissions/scope, providers, uploads/files, notifications, runtime sequences, migrations/operations, client behavior, security/privacy, acceptance scenarios, correctness/completeness evaluation, or specification-to-code conformance. Also use whenever planning or implementation discovers a missing, conflicting, changed, or implementation-incomplete product/system-design decision.
---

# Maintain Specifications

Maintain `.specs/` as the repository's professional product documentation site and sole intended product/system-design authority. Make every affected journey and runtime flow understandable without reading code, while fixing enough exact contracts for implementation without invention.

## Read first

Read in order:

1. Root `AGENTS.md` and `.agents/rules/*.md` in lexical order.
2. This file completely.
3. [Documentation standard](references/documentation-standard.md) for content, navigation, or presentation work.
4. [Rating framework](references/rating-framework.md) for every audit and after every update.
5. The smallest complete connected set of generated pages/anchors, specification sources, generator, validator, conformance logic, and affected code/tests.

Follow a flow through all data, interface, async/provider, client, security, operations, and acceptance owners. Never audit one page in isolation.

## Preserve authority and scope

- Edit only `.specs/` source modules and shared assets; never hand-edit generated HTML.
- Treat code, schemas, migrations, tests, configuration, and infrastructure as implementation evidence. Do not silently copy accidental behavior over a confirmed contract.
- For specification-only work, do not modify product code.
- Preserve unrelated changes and stable page/anchor identities.
- Do not claim specifications or software are bug-free.

## Classify each change

- **Presentation rewrite:** preserve every normative identity and contract while changing wording, hierarchy, navigation, or shell.
- **Contract clarification:** close an already-decided field, state, ownership, error, ordering, recovery, or evidence gap without changing the outcome.
- **Behavior/architecture decision:** stop, cite affected clauses, explain consumers/compatibility, recommend an option, ask the owner, then update specs first.
- **Specification-to-code reconciliation:** fix code when specs are complete; route necessary design changes through the decision gate.
- **Audit/rating:** run mechanical gates and the semantic rubric; cite evidence and deductions.

## Enforce documentation architecture

- Preserve the official shell: complete sidebar, focused article, breadcrumbs, on-page contents, related links, previous/next navigation, responsive drawer, theme, focus, and print support.
- Keep navigation entirely in the sidebar. Do not add subtabs or filter/search inputs.
- Give each independent product journey, runtime sequence, provider callback, upload/file flow, notification flow, migration/deployment flow, and recovery loop a concrete discoverable page.
- Keep overview pages as maps; focused pages own executable detail.
- Keep schemas in code blocks, not model-field tables.
- Keep one requirement register on the coverage page and one decision register on the decision page; their destinations link to focused normative owners.

## Make runtime modules understandable without code

- Give every natural backend/runtime boundary—app, service, module, package, bounded context, worker, or equivalent—one developer handbook page.
- Put a chronological developer code-flow directory before schemas and component catalogs.
- Cover every material state-changing command, scoped read, event/message consumer, schedule, provider call/callback, and reconciliation path.
- Each flow names trigger/authority; exact entry point and symbols; records read/locked/created/updated; transaction/consistency/commit; audit/outbox; after-commit event/job/provider/downstream consumer; terminal response/state; duplicates/concurrency/denials/retries/failures/operator recovery.
- Follow asynchronous and cross-module work to the terminal product outcome. Catalogs do not substitute for chronology.

## Close connected contracts

For every affected flow define or justify as not applicable:

- product actors, prerequisites, sequence, alternatives, denial, terminal outcomes, recovery, non-goals, and cross-feature effects;
- data owner, exact schemas/types/relationships/constraints/indexes/states/history/deletion/retention/migration/concurrency;
- runtime symbols, public seams, transaction/consistency boundaries, lock/order, idempotency, post-commit work, retries, and stable failures;
- sealed interface inputs/outputs/statuses/errors/metadata/pagination/version/idempotency and generated-client mapping;
- events/jobs producer/payload/version/dispatch/ordering/deduplication/consumer/retry/dead-letter/replay/observability;
- provider adapter, credentials, normalized outcomes, timeout/circuit/rate policy, callback verification, reconciliation, privacy, and telemetry;
- authority/scope, denial, private assets, sensitive data/secrets, abuse controls, and audit;
- fresh install, migration/backfill, compatibility, rollout/rollback, readiness, backup/restore, RPO/RTO, and operator recovery;
- client routes/surfaces, state owners, action authority, interaction states, accessibility, offline/reconnect/stale/schema mismatch, and evidence;
- stable scenarios with exact actors, fixtures, invocation cases, responses, durable/forbidden effects, controls, cleanup, and test mapping.

## Maintenance workflow

1. Record Git/worktree baseline and normative counts.
2. Trace the complete impact surface and assign one source owner per fact.
3. Edit source and navigation together; preserve/update anchors and inbound links.
4. Add validator/conformance checks for every contract that must not regress.
5. Run:

```bash
python3 .agents/skills/maintain-specifications/scripts/spec_quality_gate.py --repo .
```

For a complete rough cut blocked only by explicit owner decisions, run the command with `--allow-draft` and report mechanical quality separately from final completion. Final work must pass without that flag.

6. Inspect changed semantics and representative rendered pages.
7. Apply the rating framework: implementation readiness, correctness, completeness, and full-product/deferred visual score.
8. Review status/diff for secrets, local paths, placeholders, stale output, and accidental files.

## Skill integration

- `create-feature-plan` must use this skill for every missing/changed decision and every specification validation/rating/reconciliation.
- `implement-feature` must use this skill before approved contract changes and again for final specification-to-code reconciliation.
- Do not invoke implementation when the user requested specifications only.

## Definition of complete

Complete only when sources and generated pages agree; navigation/anchors are discoverable; all applicable contract dimensions are explicit; module developer flows are chronological and terminal; schemas are exact/sealed; requirements/decisions/scenarios are traceable; connected consumers agree; deterministic generation, validation, conformance, links, and visual checks pass; semantic scores are honest; and only intentional safe changes remain.
