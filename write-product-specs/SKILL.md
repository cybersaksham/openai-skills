---
name: write-product-specs
description: Create, reconstruct, expand, reconcile, or audit a complete implementation-ready product specification system and repository agent workflow. Use when Codex must turn a product prompt, PRD, notes, discussions, designs, or an existing codebase into a professional generated `.specs/` documentation site; install or update the repository-local `.agents/skills/maintain-specifications`, `create-feature-plan`, and `implement-feature` pipeline; add the minimum specification authority routing to `AGENTS.md` without replacing an existing agent harness; and expose that same harness to Claude through exact compatibility symlinks. Supports any product, language, framework, datastore, client, integration, deployment model, or repository layout.
---

# Write Product Specs

Build a specification system that a human can use to understand the complete product and that an implementation agent can use as its only product and system-design authority. Produce decisions, not decorative prose. Do not modify product code unless the user separately requests implementation after the specification workflow is complete.

## Load the applicable resources

Read these files completely before acting:

1. [Discovery and decision gate](references/discovery-and-decision-gate.md) for every run.
2. [Documentation standard](references/documentation-standard.md) before creating or changing `.specs/` structure or content.
3. [Contract coverage standard](references/contract-coverage.md) before writing product, architecture, data, transport, runtime, or acceptance contracts.
4. [Scaffold source schema](references/scaffold-schema.md) before populating a newly generated `.specs/source/` tree.
5. [Evaluation rubric](references/evaluation-rubric.md) before auditing or declaring completion.
6. [Project harness standard](references/project-harness-standard.md) before adding or updating `AGENTS.md` or `.agents/skills/`.

Inspect the target repository's instructions before installing anything. When an existing specification or harness has its own maintenance workflow, read and honor it too.

## Guarantee the output contract

Complete runs must leave the target repository with:

```text
.specs/
  source-only specification modules
  deterministic generator and validator
  generated static HTML documentation
  local CSS, JavaScript, and vector assets
.agents/skills/
  maintain-specifications/
  create-feature-plan/
  implement-feature/
AGENTS.md
.claude -> .agents
CLAUDE.md -> AGENTS.md
```

Use `.agents/skills/` as the canonical path. If the repository already uses another explicitly authoritative skill directory, preserve that convention and adapt references consistently instead of creating a competing harness.

The two relative symlinks above are the complete Claude compatibility layer. Do not create separate Claude instructions, settings, commands, hooks, skill copies, or any other Claude-specific content. If either path already exists but is not the exact expected symlink, stop and ask the owner to reconcile it; never overwrite or merge that path automatically.

The final `.specs/` must contain no scaffold placeholders or unresolved decisions. If owner input is unavailable, create the complete determinable rough cut, represent each true blocker as a named pending decision, run all possible checks, and report that completion is blocked. Never invent the missing choice to obtain a passing score.

## Choose the operating mode

- **Greenfield discovery:** derive the product from prompts, PRDs, notes, designs, and owner answers. Recommend options for missing material decisions and ask focused questions.
- **Existing-product reconstruction:** inspect current code, migrations, schemas, tests, APIs, generated clients, configuration, infrastructure, and operational artifacts. Treat them as evidence of current behavior, not automatic proof of intended behavior.
- **Hybrid reconciliation:** combine supplied intent with an implementation. Record every mismatch; ask whether product intent or implementation should change whenever the answer is not already authoritative.
- **Expansion or audit:** preserve the existing documentation shell and stable identities while closing missing flows, architecture, contracts, or evidence.

## Follow the workflow

### 1. Establish repository and authority boundaries

- Read every applicable `AGENTS.md`, repository rule, and local skill before planning edits.
- Record the current branch, commit, working-tree state, repository layout, and existing harness/specification files.
- Preserve unrelated changes. Do not switch branches, rewrite history, or replace a harness.
- Identify the actual backend, frontend/client, shared libraries, infrastructure/deployment, schemas, generated artifacts, and test locations. Treat `backend/`, `frontend/`, and deployment configuration as discovery defaults only.
- Record which inputs are owner intent, historical context, implementation evidence, or proposals.

### 2. Build the product knowledge registers

Create stable source-owned registers for:

- atomic requirements and their supplied source;
- decisions, rationale, confirmation, consequences, and affected contracts;
- product actors, authority, vocabulary, outcomes, non-goals, and journeys;
- product features and cross-feature flows;
- runtime components, modules/services/packages, data stores, interfaces, events, jobs, providers, clients, and operations;
- open questions, conflicts, superseded statements, and implementation mismatches.

Do not write pages directly from a long narrative. Normalize the knowledge first so one fact has one normative owner and every summary links back to it.

### 3. Run the decision gate

Apply the process in [Discovery and decision gate](references/discovery-and-decision-gate.md).

- Discover technical facts from the repository when possible.
- Ask only for product, experience, policy, security, data-loss, compatibility, provider, operational, or architecture choices that cannot be safely derived.
- Batch related questions and explain impact plus a recommended option.
- Continue writing unaffected contracts while answers are pending.
- Never hide a decision in prose, generator code, a plan, a test expectation, or current implementation behavior.

### 4. Scaffold without overwriting

For a repository that has no specification system, run:

```bash
python3 <skill-path>/scripts/init_product_specs.py \
  --repo <repository-root> \
  --product-name "<Product name>" \
  --tagline "<One-sentence product promise>"
```

The initializer uses only the Python standard library. It refuses to overwrite `.specs/`, any of the three project skills, `AGENTS.md`, `.claude`, or `CLAUDE.md`. It creates a root harness only when none exists. On an existing harness, it installs only non-conflicting missing assets and writes an additive routing proposal for semantic review. It creates `.claude -> .agents` and `CLAUDE.md -> AGENTS.md` only after their exact relative targets are in place.

After scaffolding:

- replace every starter source page with project-specific content;
- split pages by independently understandable product journey, runtime flow, system boundary, backend module/service, or contract;
- tailor the generated project-local skills to repository facts and commands while preserving their pipeline and decision gates;
- merge the minimal routing block into an existing `AGENTS.md` using [Project harness standard](references/project-harness-standard.md);
- add `.plans/` to the appropriate ignore file without disturbing existing groups.

For an existing `.specs/`, do not run the initializer. Preserve its source/generation model when it satisfies this skill; otherwise propose an additive migration and preserve stable URLs and anchors.

### 5. Write the documentation in reader order

Use the information architecture in [Documentation standard](references/documentation-standard.md):

1. Home and start-here authority map.
2. Product journeys and feature behavior.
3. System and runtime architecture.
4. Backend/module developer handbooks with chronological code flows.
5. Frontend/client nonvisual runtime and interaction contracts.
6. Data, API/transport, events/jobs, provider, security, operations, and deployment contracts.
7. Decisions, requirement coverage, acceptance, conformance, and audit evidence.

Every page title must identify the exact flow or contract it owns. Overview pages route; focused pages decide. Do not solve navigation growth with tabs or a filter input.

### 6. Close every implementation contract

Use [Contract coverage standard](references/contract-coverage.md) clause by clause.

- Keep database/domain schemas in code blocks using the project's native type vocabulary or an explicitly resolved schema DSL.
- Seal all public request, response, event, job, and provider payload schemas; unknown fields and values need explicit behavior.
- Document each backend module/service/app/package as a developer handbook whose code-flow directory precedes component catalogs.
- Trace every material entry path chronologically through exact symbols, reads/locks/writes, transaction/commit, audit/outbox, asynchronous or provider handoffs, terminal state, and recovery.
- Follow cross-module and asynchronous work to the terminal product outcome. “Call service,” “emit event,” or “enqueue job” is not a complete flow.
- Define stable executable scenarios for success, denial, validation, duplicate, stale, concurrent, retry, partial failure, recovery, security, and accessibility paths that apply.
- Mark a dimension `not applicable` only with a concrete reason.

“Framework-neutral” means adapting to the selected stack instead of assuming the source project's stack. It never permits vague final contracts. In an existing project, use verified exact symbols. In greenfield work, use confirmed target symbols and native contract types after architecture decisions close; keep unselected provider wire values or framework-specific seams as explicit pending decisions.

### 7. Generate and validate deterministically

Edit only specification source modules and shared assets. Never hand-edit generated HTML.

Run the installed project workflow:

```bash
python3 .agents/skills/maintain-specifications/scripts/spec_quality_gate.py --repo .
```

The gate must build twice, prove deterministic output, validate source and generated structure, run specification conformance tests, check links and stable identities, reject placeholder/pending contracts for final mode, enforce the sidebar-only documentation shell, and run `git diff --check` when Git is available.

When material owner decisions prevent finalization, run the same gate with `--allow-draft`. It must report structural/mechanical quality separately from `completion_gate_passed: false`. Never present a draft-mode pass as final specification completion.

Add project-specific validators whenever a correction, invariant, contract coverage rule, or repository comparison must never regress. Mechanical checks are necessary but cannot award semantic completeness.

### 8. Perform semantic and visual audits

- Trace representative and high-risk journeys from actor intent through client, interface, domain, persistence, event/job/provider, operations, terminal outcome, and acceptance evidence.
- Compare all normative owners for contradictions and check that every supplied requirement has a rendered destination.
- Simulate implementation: list every decision an agent would still need to make. Resolve it or record a blocking owner question.
- Visually inspect representative desktop and narrow-screen pages in the browser permitted by the target repository. Verify navigation, breadcrumbs, contents rail, anchors, tables, code, focus, responsive drawer, theme, and print behavior.
- Apply [Evaluation rubric](references/evaluation-rubric.md) honestly. Do not award credit for volume, page count, styling, or current code behavior.

### 9. Install and verify the repository pipeline

Ensure the three project-local skills form this mandatory chain:

```text
implement-feature
  -> create-feature-plan
       -> maintain-specifications for every missing or changed decision
  -> maintain-specifications again for final spec-to-code reconciliation
```

Verify `AGENTS.md` routes specification, planning, and implementation work to these skills, establishes `.specs/` as product/system-design authority, requires exact `.html#anchor` citations, and preserves repository-specific engineering rules without becoming a long duplicate of the skills.

Verify `.claude` is a relative symlink whose target text is exactly `.agents`, and `CLAUDE.md` is a relative symlink whose target text is exactly `AGENTS.md`. Reject copied harnesses, divergent Claude instructions, or additional Claude-only configuration.

### 10. Hand off evidence

Report:

- created and modified specification/harness files;
- requirement and decision status;
- page, flow, module code-flow, schema, operation, event/job/provider, and scenario counts;
- deterministic build, validation, conformance, link, and visual-audit results;
- implementation-readiness, correctness, completeness, and full-product scores;
- exact remaining assumptions, pending owner decisions, or external blockers;
- whether existing harness content was preserved and how routing was merged.

Do not claim the product or future implementation is bug-free. A 10/10 means the documented scope is decision-complete and executable, not that defects are impossible.

## Definition of complete

Finish only when:

- `.specs/` is a professional, generated, static documentation site with local assets and sidebar-only navigation;
- all supplied requirements and confirmed decisions are traceable to stable pages and anchors;
- humans can understand every product journey and system flow without opening code;
- agents can implement all in-scope behavior without inventing a product or architecture choice;
- backend/runtime module pages contain chronological developer code flows, not disconnected catalogs;
- data schemas are code-formatted and transport/event/provider contracts are sealed;
- generated output is deterministic and every applicable mechanical/conformance gate passes;
- the semantic rubric has no hidden deduction or unresolved assumption for any awarded 10;
- the three local skills and concise root harness enforce the same specification-first pipeline;
- the only Claude compatibility entries are `.claude -> .agents` and `CLAUDE.md -> AGENTS.md`;
- existing repository instructions and unrelated changes remain intact.
