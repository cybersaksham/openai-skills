# Discovery and decision gate

Use this procedure before a specification states behavior or system design. It prevents a polished document from silently converting guesses, accidental code behavior, or conflicting source material into authority.

## Classify every input

| Class | Meaning | Permitted use |
| --- | --- | --- |
| Confirmed owner intent | Current product or architecture decision from an authorized owner | May become normative after conflict checks. |
| Supplied requirement | PRD, prompt, design, policy, contract, or other declared source | Preserve and trace; resolve conflicts before finalizing. |
| Implementation evidence | Current code, migration, test, schema, runtime config, infrastructure, or observed behavior | Use to reconstruct current behavior and exact symbols; do not automatically make it intended. |
| Historical context | Superseded PRD, old plan, retired behavior, issue, or commit | Keep non-normative unless the owner reconfirms it. |
| Proposal | Agent recommendation or unapproved option | Never write as decided behavior. |

Record source identity and confidence. Never collapse implementation evidence and product intent into one statement.

## Discover before asking

Investigate facts that a repository can answer:

- languages, frameworks, versions, package boundaries, entry points, and deployment topology;
- current models, schemas, migrations, indexes, constraints, APIs, events, jobs, providers, and clients;
- code ownership, transaction boundaries, retries, tests, environment variables, and generated artifacts;
- existing instructions, decisions, terminology, and compatibility commitments.

Ask the owner only when the answer changes product behavior or selects among materially different valid designs.

## Identify decision-grade gaps

A decision is unresolved when two reasonable implementations could produce different observable, security, data, compatibility, reliability, operational, or ownership outcomes. Common examples:

- actor authority, denial semantics, tenant/scope isolation, or administrative override;
- creation, update, cancellation, deletion, retention, restoration, or irreversible data loss;
- state transitions, duplicate/concurrent behavior, late actions, partial completion, or reconciliation;
- API compatibility, public schema, versioning, pagination, idempotency, or error behavior;
- event ordering, retry/backoff, dead letter, replay, or exactly/at-least-once expectations;
- provider selection, normalized outcomes, timeout, callback trust, secret ownership, or fallback;
- frontend route, ownership of server/URL/form/local state, offline/reconnect behavior, or accessibility outcome;
- migration order, release compatibility, rollback, data recovery, availability, RPO/RTO, or operator action;
- intended behavior conflicting with the existing implementation.

Do not ask about naming or implementation placement when repository conventions make the answer discoverable and the choice does not alter a contract.

## Ask focused questions

For each unresolved decision:

1. Name the affected user or system outcome.
2. Cite the conflicting input or missing contract.
3. Explain affected features, consumers, compatibility, data, and security consequences.
4. Present a recommended option and why it best fits known constraints.
5. Ask one decision question with bounded options when possible.

Batch questions that share one decision boundary. Avoid broad questionnaires that ask the owner to redesign the system from scratch.

## Continue safely while blocked

- Write unaffected pages and contracts completely.
- Give each unresolved decision a stable id such as `DEC-AUTH-001`.
- Put the literal status `pending` in the decision register.
- At every affected clause, link to the pending decision and state known constraints without selecting an outcome.
- Make final validation fail while a material decision remains pending.
- Never use `TODO`, `TBD`, ellipses, “standard behavior,” or a hidden default as substitutes.

## Reconcile an existing implementation

When code and supplied intent differ, classify the mismatch:

| Mismatch | Action |
| --- | --- |
| Spec is complete; code is incomplete or wrong | Keep the spec; record implementation gap. |
| Code exposes a missing product/system decision | Ask the owner before making either side authoritative. |
| Owner explicitly changes intended behavior | Update specs first, then planning/implementation may follow. |
| Code contains incidental framework behavior | Document only if the owner accepts it as a contract; otherwise keep it implementation detail. |
| Existing public behavior implies compatibility risk | Explain consumers and migration path before requesting a decision. |

Use exact code symbols in developer flows only after verifying them. A symbol name is evidence; its behavior remains subordinate to confirmed specification authority.

For greenfield work, choose exact target symbols, native types, provider payloads, and deployment values only after the relevant architecture decision is confirmed. Framework-neutral discovery means selecting the project's own vocabulary instead of preselecting a framework; it never means leaving a final contract at “handler,” “service,” “payload,” or another generic label.

## Close the gate

A decision is closed only when the register contains:

- stable id and question;
- selected behavior;
- confirmation source/context;
- rationale;
- consequences and rejected alternatives where material;
- affected page/anchor, schema, state, API, event/job, provider, client, operation, test, and plan references;
- migration or compatibility effect when applicable.

Recheck every affected consumer after closure. A local edit is not reconciliation.
