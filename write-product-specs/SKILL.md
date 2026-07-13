---
name: write-product-specs
description: Create, expand, reconcile, or audit a complete static HTML product-specification system under `.specs/`. Use when Codex must turn a product idea, prompt, discussion, notes, existing documentation, or observed behavior into a standalone source of truth that explains the product to humans and fixes enough product, experience, data, runtime, client, integration, security, and testing decisions for implementation agents to build without consulting another requirements source or inventing missing behavior.
---

# Write Product Specs

Create product documentation that is simultaneously human-readable and implementation-complete. Treat the
generated HTML as the product and system-design authority, not as a task checklist or a thin feature list.

## Load the right resources

- Read [references/specification-system.md](references/specification-system.md) completely before creating a
  new `.specs/` system or changing its information architecture.
- Read [references/feature-page-contract.md](references/feature-page-contract.md) completely before writing or
  auditing feature pages.
- Read [references/audit-checklist.md](references/audit-checklist.md) completely before declaring the specs
  complete.
- Read [references/scaffold-schema.md](references/scaffold-schema.md) when populating the bundled generic
  scaffold; it defines every source key and tuple shape expected by the renderer and validator.
- For a new repository with no `.specs/`, run `scripts/init_specs.py`. Do not run it over an existing
  `.specs/`; inspect and evolve the existing generator instead.

## Non-negotiable outcome

The final `.specs/` must stand on its own:

- A human can understand what the product is, who it serves, why each capability exists, and every user flow.
- An implementation agent can identify the intended repository structure, ownership boundaries, data model,
  commands, reads, interfaces, states, failures, permissions, jobs, and tests without making a product or
  system-design decision.
- The authoritative runtime, interaction-surface, data, interface, event, integration, operations, and
  experience descriptions represent the same behavior.
- Every supplied requirement is present, reconciled, and traceable; no outside artifact is required to
  interpret it.
- Unknown material decisions are resolved with the owner before the documentation is called final.

Do not assume a product category, architecture style, programming language, framework, database, cloud,
provider, repository shape, or release model. Derive them from the task and repository. When a required choice
is absent, recommend options and ask the owner; do not hide a choice inside the documentation.

## Choose the operating mode

1. **Create:** no specification system exists. Discover the product, initialize `.specs/`, then fill it.
2. **Expand:** documentation exists but a feature, flow, or technical layer is missing. Preserve the current
   structure and add the smallest coherent documentation slice.
3. **Reconcile:** a discussion, decision, implementation change, or owner correction makes the current specs
   stale. Update the source modules, regenerate HTML, and check all downstream contracts.
4. **Audit:** inspect the complete system for omissions, contradictions, hidden decisions, and insufficient
   code architecture; fix findings when the user authorized changes.

## Workflow

### 1. Orient before writing

- Read repository instructions and inspect existing code/documentation when present.
- Inventory all information supplied in the request and attached workspace.
- Identify product scope, actors, outcomes, feature candidates, cross-feature workflows, known constraints,
  explicit exclusions, and already-made decisions.
- Separate observed facts from proposals and unresolved choices.

### 2. Build the requirement and decision registers

- Convert every meaningful input clause into an atomic, stable requirement id.
- Record its source reference, source wording or a lossless paraphrase, affected feature/cross-cutting area,
  destination section, and status.
- Record conflicts and superseded statements explicitly; never silently select one.
- Maintain a decision register containing the chosen behavior, rationale, confirmation context, consequences,
  and affected pages.
- Batch focused owner questions around decisions that materially alter product behavior, UX, data, security,
  integrations, architecture, or scope. Continue drafting unaffected areas while answers are pending.
- Missing owner choices never justify returning an untouched scaffold. Populate every determinable page and
  feature. At each affected point, reference a decision whose literal status is `pending` and document the
  known constraints and consequences without selecting an answer. Never use `pending while drafting` as a
  status value.

An incomplete rough cut is still fully authored: every known flow and contract is documented, and every true
gap is represented by an explicit `pending` requirement or decision row. Final documentation contains no
`pending` row.

### 3. Model the product before its screens

- Define the product promise, actors, vocabulary, feature taxonomy, information architecture, and end-to-end
  journeys.
- Identify shared domain spines and cross-cutting concerns before duplicating them across features.
- Establish ownership: which domain owns truth, which layers adapt it, and which consumers receive contracts
  or events.
- Define scope boundaries and explicit non-goals so future possibilities do not leak into current behavior.

### 4. Establish the documentation system

For a new system, run:

```bash
python3 <skill-path>/scripts/init_specs.py \
  --root <product-repository> \
  --product-name "<Product name>"
```

The bundled generator requires Python 3.10 or newer and only the standard library. This documentation-tooling
choice does not constrain the product's implementation stack.

Then replace every scaffold placeholder by editing underscore-prefixed source modules. Never hand-edit
generated HTML. The scaffold builds immediately but its validator intentionally fails until placeholders,
feature manifests, requirements, and decisions are complete. For an existing system, preserve its generator,
navigation, styling, and source conventions unless the requested change requires an information-architecture
correction.

If owner input cannot arrive in the current task, still generate the complete rough cut, run the build and
validator, and hand off the deliberate validation failures with the exact questions needed to reach final.
Use “Pending owner decision `DEC-…`” rather than leaving `TODO` placeholders.

### 5. Write product documentation, not an implementation ticket

- Lead each page and feature with purpose, people, goals, and flows.
- Explain why a feature exists and what outcome it creates before technical details.
- Use clear narrative, diagrams/flow blocks, tables, and nested navigation rather than a wall of requirements.
- Keep imperative work instructions, estimates, assignees, and sprint language out of the product docs.
- Make technical sections precise without turning the whole site into a build contract.

### 6. Make every feature code-centric

Apply the complete feature contract from `references/feature-page-contract.md`. Define both behavior and
implementation shape: domain ownership, records and constraints, command/read contracts, transactions,
permissions, interfaces, interaction surfaces/state, events/jobs, errors, edge cases, migrations,
observability, operations, and test obligations. Specialize terminology to the chosen architecture; do not
force an authoritative-runtime/interaction-surface split where the product genuinely uses another shape.

### 7. Define cross-cutting architecture

Document repository layout, runtime boundaries, dependency direction, shared primitives, identity/access,
data conventions, interface conventions, asynchronous work, integrations, security/privacy, observability,
testing, environments, configuration, migrations, rollout, recovery, operational ownership, and
implementation sequence. Integration and operations coverage is required unless the owner explicitly excludes
it. Pin exact technologies and versions only after they are known or decided.

The default cross-cutting pages are a coverage topology, not a prescribed product architecture. Split or
combine pages and source modules when the real product boundaries demand it, while retaining every required
concern. Never invent a runtime, interaction layer, datastore, integration, or deployment layer merely to fill
the template; document why a concern is inapplicable or explicitly excluded.

### 8. Generate and mechanically validate

Run the repository's commands. The generic scaffold uses:

```bash
python3 .specs/_build.py
python3 .specs/_validate.py
```

Validation must cover expected pages/sections, duplicate ids, broken relative links, feature-manifest parity,
unique contract identities, requirement destinations, unresolved decisions, stale claims, and placeholders.
Add product-specific regression assertions whenever a correction must never return.

### 9. Perform semantic and visual audits

- Follow `references/audit-checklist.md` clause by clause.
- Compare every requirement id with its rendered destination.
- Trace each end-to-end journey across experience, interfaces, runtime execution, data, events/jobs,
  integrations, operations, permissions, failures, and tests.
- Simulate implementation by asking what decision a coding agent would still need to make. Resolve every
  answer in the specs.
- Render representative overview, architecture, dense feature, table-heavy, and mobile pages. Verify nested
  navigation, search, anchors, overflow, typography, and print behavior.

### 10. Close with evidence

Report generated pages, decisions resolved, remaining explicit blockers, build/validation results, and visual
checks. Do not call the system final while any required clause, material choice, or cross-page mismatch remains.

## Editing discipline

- Keep authored source and generated HTML in `.specs/`; distinguish source modules with a leading underscore.
- Keep assets local and relative so `index.html` opens directly without a server.
- Preserve stable page names, section anchors, feature slugs, state names, error codes, event names, and model
  identities once implementation can depend on them.
- Change shared contracts first, then update every feature and reference page that consumes them.
- When reality and documentation differ, determine which is authoritative. If behavior/design must change,
  update the specs deliberately; never make the docs merely describe an accidental implementation.
- Keep specs and code synchronized during later implementation. A passing test suite does not excuse a code
  structure or feature flow that contradicts the relevant specs.
