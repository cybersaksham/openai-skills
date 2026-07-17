# Specification implementation-readiness rubric

Rate whether the generated `.specs/` can serve as the only product and system-design authority for an implementation agent. Score documented decisions, consistency, discoverability, and executable evidence—not prose volume, page count, styling, or resemblance to current code.

## Contents

- [Required scores](#required-scores)
- [Weighted categories](#weighted-categories)
- [Category scoring anchors](#category-scoring-anchors)
- [Hard caps](#hard-caps)
- [Evidence procedure](#evidence-procedure)
- [Required report](#required-report)

## Required scores

Always report:

1. **Implementation readiness excluding approved visual design** — normalize applicable nonvisual categories to 10.
2. **Correctness** — whether normative owners agree, identities preserve one meaning, summaries do not contradict focused owners, and no impossible/unsafe combination is required.
3. **Completeness** — whether every in-scope actor, branch, field, schema, state, owner, failure/recovery path, operation, effect/non-effect, operational value, and evidence obligation exists without code archaeology or invention.
4. **Full product delivery readiness** — report `deferred` until authoritative page-level visual designs exist; otherwise include visual design in the full score.

Round final scores to one decimal. A direct contradiction prevents correctness 10. Any silent applicable dimension, open/inferred public schema, unresolved data type, generic scenario, undefined operational value, or pending decision prevents completeness 10.

## Weighted categories

| Category | Weight | Full-credit evidence |
| --- | ---: | --- |
| Product behavior and end-to-end flows | 13 | Every actor, precondition, entry, sequence, alternative, denial, terminal state, recovery, non-goal, and cross-feature effect is explicit. |
| Domain model and data lifecycle | 12 | Code-format schemas close fields/types, constraints/indexes, relationships, states, history/versioning, deletion, retention, migration, and concurrency. |
| Backend/runtime architecture and ownership | 11 | Every natural module/service/app/package has chronological developer flows from trigger/authority through exact symbols, data and consistency effects, handoffs, terminal state, errors, and recovery; catalogs close signatures. |
| API/interface and generated-client contracts | 10 | Every operation has sealed input/output, statuses/outcomes, errors, headers/metadata, pagination/version/idempotency behavior, and generated-client mapping where applicable. |
| Authorization, scope, security, and privacy | 10 | Authority, scoped reads, denial, sensitive data/assets, secrets, abuse controls, and audit are consistently defined on every path. |
| Events, jobs, ordering, and reliability | 8 | Producer, payload/version, dispatch, consumer, ordering, deduplication, retry, dead letter, replay, compatibility, and observability are explicit. |
| Provider and external integration boundaries | 7 | Adapter, credentials, normalized outcomes, timeout/circuit/rate policy, callback security, reconciliation, privacy, and safe telemetry are exact. |
| Bootstrap, migrations, deployment, and operations | 7 | Fresh install, upgrade/backfill, compatibility, rollout/rollback, readiness, backup/restore, RPO/RTO, observability, and operator recovery are executable. |
| Client nonvisual runtime and accessibility | 7 | Route/surface and state owners, DTO/action authority, interaction states, error/reconnect/stale/schema mismatch, semantics, keyboard/focus, and evidence are closed. |
| Acceptance, conformance, and testability | 8 | Stable scenarios contain exact authority, fixtures, cases, response/effects/non-effects, time/concurrency/failure controls, cleanup, and reproducible evidence. |
| Documentation architecture and discoverability | 4 | Sidebar titles expose concrete journeys/system flows; overview/detail ownership, anchors, related links, compatibility, and code-flow directories are complete. |
| Page-level visual design | 3 | Authoritative responsive designs fix layout, content hierarchy, component states, interaction affordances, and accessibility for each product surface. |
| **Total** | **100** | |

When visual design is explicitly deferred:

```text
implementation_readiness = earned_nonvisual_points / 97 * 10
```

Otherwise:

```text
full_readiness = earned_points / 100 * 10
```

## Category scoring anchors

| Score | Meaning |
| ---: | --- |
| 0 | Missing or contradicts the documented product. |
| 5 | Direction exists, but implementation requires major choices or code archaeology. |
| 7 | Main path is implementable; material edge, failure, security, integration, or operational decisions are absent. |
| 8 | Strong contract; a few bounded assumptions or evidence gaps remain. |
| 9 | Decision-complete for normal implementation; only low-risk precision, discoverability, or proof gaps remain. |
| 10 | No undocumented implementation choice remains in scope; connected contracts agree; stable executable evidence can prove every material branch. |

Use 0.5 increments at smallest. A 9.5 requires a named minor deduction. A 10 requires an explicit no-deduction finding.

## Hard caps

Apply the lowest relevant cap:

- Build, deterministic generation, validation, conformance, or broken-link failure: overall readiness at most **7.0**.
- Unresolved product, policy, security, data-loss, provider-secret, or compatibility decision: affected category at most **5** and overall at most **7.5**.
- Missing request/response/error, legal transition, migration, retry/idempotency, or material acceptance branch: affected category at most **8**.
- Public operation/event/job/provider payload is open, inferred, or missing a sealed schema: interface category and overall at most **8**.
- Data field/type/null/default/relationship/constraint/index behavior is unresolved: domain category and overall at most **8**.
- Stable scenarios use generic actors/pre-states/outcomes or omit response, forbidden effects, time/concurrency, cleanup, layer, or evidence: acceptance category and overall at most **8**.
- Major cross-system journey exists only as scattered component prose: product/runtime/reliability categories at most **8**.
- Runtime module contains disconnected model/service/API/event/job catalogs but no chronological developer flows: runtime category and overall at most **8**.
- Current code or tests are required to discover intended behavior: affected category at most **8**.
- Contradictory normative owners or lost page/anchor compatibility: documentation and affected categories at most **7**.
- Undefined rollout thresholds, observation windows, backup/restore, RPO/RTO, or operator recovery: operations category at most **8**.
- Page-level design deferred: full-product score remains **deferred**.

Overall 10 is impossible if any category is below 10, any applicable dimension is silently absent, any mechanical gate fails, or any unresolved assumption remains.

## Evidence procedure

1. Run the project specification quality gate and retain metrics. A rough cut may use `--allow-draft` to prove mechanical structure, but final readiness requires `completion_gate_passed: true` without draft mode.
2. Trace representative normal and high-risk flows across product, data, runtime, interface, async/provider, client, security, operations, and acceptance pages.
3. Inspect every category changed and every shared consumer.
4. Cite current generated `.specs/*.html#anchor` evidence for every category and every deduction.
5. Compare stable requirements, decisions, flows, schemas, operations, events/jobs/providers, module code flows, scenarios, and anchors to a recorded baseline when available.
6. Search for contradictory summaries, open/inferred schemas, generic placeholders, undefined operational values, and stale compatibility text.
7. Assign correctness and completeness independently, then category scores and caps.
8. List the smallest concrete changes needed to remove every deduction.

## Required report

```markdown
Specification readiness: <score>/10 excluding approved visual design
Correctness: <score>/10
Completeness: <score>/10
Full product delivery readiness: deferred | <score>/10
Mechanical gate: pass | fail
Baseline comparison: <previous score or unavailable> -> <current score>

| Category | Weight | Score | Evidence and deduction |
| --- | ---: | ---: | --- |
| Product behavior and end-to-end flows | 13 | 9.0 | `.specs/...html#...`; missing ... |

Hard caps applied: none | <cap and cause>
Remaining assumptions:
- None.

Highest-value improvements:
1. <specific missing contract and owner page>
```

Never claim “bug-free.” A 10 means decision-complete and executable within documented scope.
