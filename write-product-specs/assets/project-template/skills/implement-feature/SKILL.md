---
name: implement-feature
description: Implement this repository's features end to end from specification-backed planning through production-grade code, tests, integration, and final specification-to-code reconciliation. Use when a user asks to build, add, complete, or implement behavior spanning any backend/runtime, client, data, interface, event/job, provider, security, migration, deployment, or shared platform area. Use `$create-feature-plan` for every plan and `$maintain-specifications` for every product/system-design decision, update, validation, rating, or reconciliation.
---

# Implement Feature

Own a feature from requested outcome to verified integration. Execute only ready specification-backed plans and finish only when implementation and specifications agree.

## Boundaries

- Read `../create-feature-plan/SKILL.md` before creating/revising plans.
- Read `../maintain-specifications/SKILL.md` before every specification decision/edit and during final reconciliation.
- Treat `.specs/` as intended product/system-design authority; code is implementation evidence.
- Do not implement until prerequisite plans are ready and decisions resolved.
- Keep plans in `.plans/`, contracts in `.specs/`, and code/tests in owning paths.
- Preserve unrelated changes, stay on the current branch unless directed, and keep commits coherent.
- Never claim bug-free; complete only with no known defect, untested specified branch, failing applicable gate, or unresolved conformance row.

## Workflow

1. Identify the complete feature boundary: actors, entry points, authority, data lifecycle, client surfaces, async work, providers, security, failures/recovery, consumers, and terminal outcomes.
2. Use `$create-feature-plan` for one bounded plan or a dependency graph with `00-integration`. Prefer vertical outcomes over backend/frontend batches.
3. Review all plans through the specification gate. Stop dependent work for missing/conflicting/changed behavior; update/rebuild/validate/rate specs through `$maintain-specifications` first.
4. Execute sequentially by default. Parallelize only proven disjoint write sets with stable contracts and explicit shared owners.
5. Implement one slice at a time with its tests, migrations, generated artifacts, permissions, errors, client states, accessibility, security/privacy, observability, and operations. Run decisive checks immediately and update plan evidence.
6. If implementation exposes a design choice, stop and return to the specification decision gate. If code merely fails a complete spec, fix code/tests without changing the contract.
7. Run all applicable static/type/format/build, migration/database, unit, permission, interface/event/provider, client, concurrency/idempotency/retry/recovery, security/privacy/accessibility, integration/end-to-end, reliability/performance, generated-drift, and regression gates.
8. Before completing each plan and the integrated feature, use `$maintain-specifications` to reread every current clause and map ownership, symbols, schemas, states, transactions, interfaces, errors, async/provider behavior, routes/surfaces, security, operations, non-goals, and scenarios to actual code/migrations/generated artifacts/tests.
9. Fix every implementation mismatch, route every necessary design change through the decision gate, rerun affected gates, run the specification quality gate and semantic rating, and resolve every conformance row as `matched` or specification-backed `not applicable`.
10. Run the integration plan, inspect the final diff for secrets/local paths/accidental files/stale output/architecture violations, and report outcomes, checkpoints, tests, spec synchronization, risks, and true external blockers.

## Definition of complete

Complete only when all plans/slices and dependencies are complete; every applicable pipeline passes; migrations and generated artifacts are current; specified success/denial/error/retry/concurrency/recovery/accessibility/security/privacy paths are proven; all spec decisions reach every consumer; every conformance row resolves; and the final repository state contains only intentional safe changes.
