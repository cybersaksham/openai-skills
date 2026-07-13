# Generic scaffold schema

Use these exact structures with the bundled scaffold. Values below describe shape only; replace them with
product-specific, decision-resolved content.

## Contents

1. Feature product definition
2. High-level system design
3. Low-level code architecture
4. Route or surface manifest
5. Event or message manifest
6. Requirement coverage register
7. Decision register
8. Cross-cutting pages

## Feature product definition

Add one dictionary to `_features.py`:

```python
FEATURES = [
    {
        "slug": "stable-feature-slug",
        "name": "Human feature name",
        "group": "One value from FEATURE_GROUPS",
        "status": "Current scope/status in human language",
        "summary": "One-paragraph capability summary.",
        "why": "Problem, harm, and value.",
        "goals": ["Outcome"],
        "non_goals": ["Explicit exclusion"],
        "personas": [("Actor", "Need, authority, and responsibility")],
        "success_metrics": [("Signal", "Meaning, target, or guardrail")],
        "dependencies": ["Prerequisite and dependency type"],
        "flows": [("Flow name", "Initiating actor", "Ordered user/system flow including recovery")],
        "screens": [("Screen or surface", "Actor", "Content, actions, validation, and every state")],
        "states": ["stable_state_name"],
        "models": [("Conceptual model", "Product fields", "Ownership and constraints")],
        "permissions": [("Action or read", "Actor", "Scope, object rule, denial, and audit")],
        "rules": ["Product invariant"],
        "edge_cases": ["Edge/failure/race case"],
        "acceptance": ["Externally provable behavior"],
        "future": "Extension seams and explicit deferred boundaries.",
    }
]
```

All fields are required and nonempty. Use an explicit “not applicable because …” statement only when a layer
truly does not exist; never add fake architecture to satisfy the validator.

## High-level system design

Add the matching slug to `_system_design.py`:

```python
SYSTEM_DESIGN = {
    "stable-feature-slug": {
        "architecture": "Ownership, source of truth, runtime and sync/async boundaries.",
        "runtime_flow": [
            ("Flow/command", "Owning module or component", "Validation through terminal behavior")
        ],
        "interaction_flow": [
            ("Actor interaction flow", "Owning surface or entrypoint", "Load/state/command/recovery behavior")
        ],
        "commands": [
            ("Command", "Actor", "Guards", "Transactional writes and asynchronous effects")
        ],
        "queries": [
            ("Query", "Visibility scope", "Projection, filters, order, freshness, and performance")
        ],
        "transitions": [
            ("Aggregate", "From", "Trigger and guard", "To", "Effects and invariant")
        ],
        "contracts": [
            ("Contract", "Shape or input", "Consumer", "Ownership/boundary rule")
        ],
        "reconciliations": [
            ("Ambiguous or historical statement", "Status", "Current meaning or decision id")
        ],
        "tests": ["Feature-specific verification obligation"],
    }
}
```

Transition identity is the composite `(aggregate, from, trigger/guard)`. Repeating an aggregate across its
state machine is expected. Screen and permission identities similarly include actor as well as surface/action.

Use `interaction_flow` for every human, operator, device, conversational, or programmatic surface. When no
separate interaction runtime exists, document the real entrypoint and why no additional boundary exists.

## Low-level code architecture

Add the matching slug to `_low_level_design.py`:

```python
LOW_LEVEL_DESIGN = {
    "stable-feature-slug": {
        "files": [
            ("exact/path/or.module", "Owned responsibility")
        ],
        "records": [
            (
                "storage identity",
                "code model identity",
                "exact fields, types, defaults, nullability, relationships",
                "constraints, indexes, deletion, history, and tenant invariant",
            )
        ],
        "commands": [
            (
                "typed_or_language_appropriate_signature",
                "authorization, validation, lock/transaction, idempotency, writes, effects, output",
                "stable_error_codes",
            )
        ],
        "queries": [
            (
                "typed_or_language_appropriate_signature",
                "scope, filters/order/page, projection/redaction, freshness, performance",
            )
        ],
        "interfaces": [
            ("method/topic/operation", "input/auth/idempotency", "success shape", "failures/authority")
        ],
        "interaction_modules": [
            ("exact/interaction/path/or.module", "State, interaction, adaptation, and test responsibility")
        ],
        "jobs": [
            ("job_or_consumer_signature", "trigger", "dedupe, authority, retry, terminal, replay, telemetry")
        ],
        "migrations": [
            ("change or migration sequence", "backfill, compatibility, rollback, and proof")
        ],
        "telemetry": [
            ("signal name", "attributes, cardinality, and privacy", "alert, dashboard, or operational response")
        ],
        "errors": ["stable_error_code — meaning, layer/status, retryability, user handling"],
    }
}
```

`interaction_modules` and `jobs` may be empty when genuinely inapplicable. All other collections must be
nonempty. For a new datastore, the migration contract still identifies initial-schema order and proof even
when no backfill is needed. For a non-persisted feature, use an explicit not-applicable record and migration
row that explains the real source of state; never invent storage to satisfy the validator. Use the existing
contract, interface, migration, telemetry, and error rows to capture feature-specific integration and
operations detail; the cross-cutting integration and operations pages remain mandatory unless explicitly
excluded.

## Route or surface manifest

In `_routes.py`, use one row per navigable or independently rendered surface:

```python
ROUTES = {
    "stable-feature-slug": [
        (
            "/stable/route or surface identity",
            "exact owning file/module",
            "screen contract and actor",
            "loading|empty|ready|pending|success|error|forbidden|retry states",
        )
    ]
}
```

An empty list is valid only when the feature has no route or user/operator surface.

## Event or message manifest

In `_events.py`, use one row per published domain event/message:

```python
EVENTS = {
    "stable-feature-slug": [
        (
            "feature.event.v1",
            "producer command/service",
            "{safe, versioned, minimal payload shape}",
            "consumer(s) and exact effect",
        )
    ]
}
```

An empty list is valid only when the feature publishes no event/message. Jobs internal to the feature still
belong in its low-level `jobs` list.

## Requirement coverage register

In `_requirements.py`:

```python
REQUIREMENTS = [
    {
        "id": "REQ-001",
        "source": "Prompt clause, discussion, document location, or observed behavior",
        "text": "Lossless requirement text or paraphrase.",
        "kind": "behavior|architecture|constraint|quality|exclusion|decision",
        "area": "Feature or cross-cutting area",
        "destinations": ["features/stable-feature-slug.html#flows"],
        "status": "covered",  # covered | superseded | pending
        "notes": "Interpretation, conflict, or superseding decision id.",
    }
]
```

Every destination must include a page and section anchor. The exact drafting status literal is `pending`;
never write `pending while drafting` as a value. Final validation rejects `pending`.

## Decision register

```python
DECISIONS = [
    {
        "id": "DEC-001",
        "question": "Material question that required a choice.",
        "choice": "Confirmed behavior or design.",
        "rationale": "Why this option fits goals and constraints.",
        "consequences": "Affected flows, data, interfaces, security, and future boundary.",
        "affected": ["feature-slug", "system-architecture.html#ownership"],
        "confirmation": "Owner-confirmed in the current task or another durable decision source.",
        "status": "confirmed",  # confirmed | pending
    }
]
```

The exact unresolved decision status literal is `pending`; never write `pending while drafting` as a value.
Final validation rejects non-confirmed rows. Update every affected source module when a decision changes.

## Cross-cutting pages

Replace scaffold content in `_pages.py` without changing stable filenames or required section ids unless the
information architecture is deliberately revised along with `_manifest.py`, `_build.py`, and `_validate.py`.
The generator appends normalized catalogs to decisions, coverage, data dictionary, permissions, interfaces,
events/jobs, audit, and overview pages; do not hand-maintain duplicate catalog rows in page prose.

The default source modules and pages express coverage, not a mandatory product topology. Split or combine them
when the actual architecture requires it, and update manifest, renderer, and validator together. Do not invent
a runtime, interaction layer, datastore, or integration solely to populate a collection. Regardless of
topology, document integrations plus environments, configuration, rollout, recovery, and operational ownership
unless the owner explicitly excludes those concerns.
