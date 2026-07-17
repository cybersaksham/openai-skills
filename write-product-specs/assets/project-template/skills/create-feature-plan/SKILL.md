---
name: create-feature-plan
description: Create or revise specification-driven implementation plans under `.plans/` for this repository's features and behavior-affecting changes. Use when a user asks for a feature/change plan, when `$implement-feature` needs decomposition, or before implementing work spanning product, backend/runtime, client, data, interface, event/job, provider, security, migration, deployment, or testing. Use `$maintain-specifications` for every specification gap, decision, update, validation, rating, or reconciliation found during planning.
---

# Create Feature Plan

Turn one requested outcome into an implementation-ready plan whose requirements come from `.specs/`, whose implementation impact is grounded in the repository, and whose completion can be proven.

## Boundaries

- Keep plans only under ignored `.plans/`; plans are working state, not product authority.
- Read `../maintain-specifications/SKILL.md` completely whenever specifications are involved.
- Do not implement code during planning unless the user separately asks.
- Treat generated `.specs/*.html#anchor` clauses as intended behavior/design; code/tests only show implementation state.
- Ask only for unresolved product, policy, experience, security, compatibility, or architecture decisions. Investigate technical facts directly.
- Never hide an assumption. A plan with an unresolved decision is `blocked_specification`.

## Workflow

1. Restate one bounded outcome, actors, entry points, terminal states, and non-goals. Record the current commit baseline.
2. Read the complete connected specification flow: feature/journey, data, runtime module/code flows, interface, events/jobs/providers, permissions/security, client, operations, and acceptance.
3. Cite exact `.specs/*.html#anchor` clauses. For persistence/transport work cite exact code-format schemas and sealed payloads. Carry stable scenario ids and their concrete controls/evidence into the plan.
4. Inspect current code, schemas, migrations, generated artifacts, tests, configuration, and infrastructure to identify the implementation gap.
5. Run the decision gate. If a contract is missing/conflicting/changed, block the plan, cite affected clauses/consumers, ask the focused question, and use `$maintain-specifications` to update/rebuild/validate/rate specs before planning resumes.
6. Choose one bounded plan or a `00-integration` plan plus numbered tracks. Allow parallel execution only for proven disjoint write sets with one owner for every shared/migration/generated artifact.
7. Design vertical, independently verifiable slices. Each slice names exact write set/symbols, behavior, authority, data, failures, concurrency/idempotency/retries, migrations/interfaces/events/providers/client/accessibility/security/operations, tests, commands, and dependencies.
8. Define the ordered release-blocking pipeline: spec update, implementation, narrow/full testing, and clause-by-clause spec-to-code reconciliation.

## Required plan format

```markdown
# <Plan title>

- Status: draft | blocked_specification | ready | in_progress | verifying | complete
- Scope: <bounded outcome>
- Spec baseline: <commit>
- Depends on: <plans/prerequisites or none>

## Outcome and non-goals
## Specification references
## Specification interpretation
## Questions and specification blockers
## Current implementation gap
## Impact and ownership
## Execution slices
### Slice 1 — <runnable outcome>
- Write set:
- Behavior and failures:
- Tests:
- Verification:
## Acceptance traceability
| Spec clause/scenario | Required outcome | Implementation target | Test/evidence |
| --- | --- | --- | --- |
## Test and quality pipeline
## Specification-to-code conformance
| Spec clause | Required structure/behavior | Actual file/symbol | Evidence | Verdict |
| --- | --- | --- | --- | --- |
## Dependencies and execution order
## Completion evidence
```

## Readiness gate

Set `ready` only when every required decision exists; cited anchors and scenarios are complete; connected effects are reconciled; exact write sets and ownership are known; slices/tests/commands are concrete; sealed schemas are traced without inferred fields; and no unresolved assumption remains. Keep the plan current during execution and return to the decision gate on behavioral drift.
