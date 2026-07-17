# Project harness standard

Install a concise repository router plus three detailed local skills. Keep repository policy close to the repository without copying the same workflow into multiple files.

## Contents

- [Canonical structure](#canonical-structure)
- [Additive installation rules](#additive-installation-rules)
- [Claude compatibility aliases](#claude-compatibility-aliases)
- [Root AGENTS.md responsibilities](#root-agentsmd-responsibilities)
- [Required skill chain](#required-skill-chain)
- [Authority boundary](#authority-boundary)
- [Verification](#verification)

## Canonical structure

```text
AGENTS.md
.claude -> .agents
CLAUDE.md -> AGENTS.md
.agents/
  rules/                         # optional repository-specific mandatory rules
  skills/
    maintain-specifications/
      SKILL.md
      references/
        documentation-standard.md
        rating-framework.md
      scripts/
        spec_quality_gate.py
    create-feature-plan/
      SKILL.md
    implement-feature/
      SKILL.md
.plans/                          # ignored local implementation state
.specs/                          # tracked authority and generated documentation
```

Use `.agents/skills/` unless an existing repository has one deliberate, authoritative alternative. Never create `.agent/skills/` and `.agents/skills/` as competing copies.

## Claude compatibility aliases

Expose the canonical harness to Claude with exactly two repository-root entries:

```text
.claude -> .agents
CLAUDE.md -> AGENTS.md
```

Both must be relative symbolic links with exactly the target text shown. They are aliases, not alternative owners. Do not copy the harness, write separate Claude instructions, or add Claude-specific settings, commands, hooks, skills, or other content.

Before making any scaffold changes, inspect both paths with symlink-aware checks. An existing exact alias is valid and must be preserved. If either path is a real file/directory or points anywhere else, stop and ask the owner to reconcile it. Never delete, replace, merge, or write through a conflicting path automatically.

## Additive installation rules

Before writing:

1. Read all effective `AGENTS.md` files and repository rule/skill directories.
2. Inventory existing skill names, triggers, precedence, branch/commit rules, and definition of complete.
3. Detect uncommitted changes and preserve them.
4. Determine whether one root harness or scoped nested harnesses are intentional.

When `AGENTS.md` exists:

- never replace or regenerate the whole file;
- add the smallest coherent specification-workflow routing block;
- retain every existing instruction and section ordering where possible;
- reconcile duplicate authority, plan locations, branch rules, commit rules, and completion definitions;
- ask the user before resolving a semantic conflict that would change existing agent behavior;
- do not add nested harnesses unless the repository already requires them or the user approves them.

When a target skill directory exists:

- do not overwrite it;
- compare its contract with the bundled template;
- preserve repository-specific commands and conventions;
- merge missing decision gates, authority rules, cross-skill calls, evaluation, and completion checks;
- ask before replacing a deliberately different workflow.

## Root AGENTS.md responsibilities

Keep the root file short enough to load on every task. It should contain only:

1. Scope and effective harness boundary.
2. Required reading order.
3. Always-on repository rule routing.
4. Automatic triggers for the three local skills.
5. `.specs/` authority and decision-gate rules.
6. Plan location and working-tree/branch discipline.
7. Repository-specific engineering/security baseline that truly applies everywhere.
8. Compact definition of complete.

Move detailed procedures, templates, rubrics, and long checklists into skills or `.agents/rules/`.

## Required skill chain

### maintain-specifications

Owns:

- specification authority and decision gate;
- documentation information architecture and presentation;
- source-only edits and deterministic generation;
- contract completeness and connected-consumer reconciliation;
- mechanical quality gate and semantic rating;
- final spec-to-code comparison.

It must trigger automatically for every `.specs/` task and whenever planning or implementation discovers or changes a product, data, API, event, permission, provider, runtime, migration, client, security, acceptance, or documentation contract.

### create-feature-plan

Owns:

- outcome decomposition and plan topology;
- exact `.specs/*.html#anchor` references;
- current implementation gap analysis;
- write-set/dependency ownership;
- vertical slices, test pipelines, and conformance rows;
- blocking any plan with unresolved specification decisions.

It must call `maintain-specifications` for every gap, change, validation, rating, or reconciliation.

### implement-feature

Owns:

- complete execution of plans and dependency graphs;
- incremental implementation and tests;
- migrations/generated artifacts/integration;
- production-quality gates;
- final specification-to-code reconciliation.

It must use `create-feature-plan` for every plan and `maintain-specifications` before approved contract changes and again before completion.

## Authority boundary

- Generated `.specs/*.html#anchor` clauses are intended product and system-design authority.
- Specification source modules are the only editable authority; generated HTML is never hand-edited.
- Code and tests prove implementation state but cannot silently override specs.
- Plans live under ignored `.plans/`; they are execution state, not requirements.
- If behavior or architecture is missing or contradictory, stop dependent work, ask the focused owner question, update specs, regenerate, validate, rate, then plan or implement.

## Verification

After installation:

- confirm all paths referenced by `AGENTS.md` exist;
- validate every local skill package;
- run the specification quality gate;
- search for stale old paths or duplicate skill owners;
- verify `readlink .claude` is exactly `.agents` and `readlink CLAUDE.md` is exactly `AGENTS.md`;
- verify no separate Claude harness or Claude-only configuration was introduced;
- prove `.plans/` is ignored and `.specs/` is tracked as intended;
- verify existing harness text and unrelated changes remain intact.
